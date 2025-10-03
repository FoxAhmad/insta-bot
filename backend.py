#!/usr/bin/env python3
"""
FastAPI Backend for Instagram Messaging Bot
Provides REST API endpoints for the web frontend.
"""

import os
import json
import asyncio
import logging
import uuid
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class LoginRequest(BaseModel):
    username: str = Field(..., description="Instagram username")
    password: str = Field(..., description="Instagram password")
    verification_code: Optional[str] = Field(None, description="Verification code if required")
    challenge_url: Optional[str] = Field(None, description="Challenge URL if verification is required")

class SessionInfo(BaseModel):
    session_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime

class MessageRequest(BaseModel):
    usernames: List[str] = Field(..., description="List of usernames to message")
    message: str = Field(..., description="Message to send")
    delay_range: List[int] = Field(default=[30, 60], description="Delay range in seconds")

class BotStatus(BaseModel):
    is_logged_in: bool
    username: Optional[str] = None
    last_activity: Optional[str] = None

class MessageResult(BaseModel):
    username: str
    success: bool
    error: Optional[str] = None

class ChallengeResponse(BaseModel):
    requires_verification: bool
    challenge_type: str
    challenge_url: Optional[str] = None
    phone_number: Optional[str] = None
    message: str

class BotResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    challenge: Optional[ChallengeResponse] = None

# Session management
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour timeout
        
    def create_session(self, username: str) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.sessions[session_id] = {
            'username': username,
            'created_at': now,
            'last_activity': now,
            'expires_at': now + timedelta(seconds=self.session_timeout),
            'bot_manager': InstagramBotManager()
        }
        
        logger.info(f"Created session {session_id} for user {username}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID if it exists and is not expired."""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        # Check if session is expired
        if datetime.now() > session['expires_at']:
            logger.info(f"Session {session_id} expired, removing")
            del self.sessions[session_id]
            return None
            
        return session
    
    def update_activity(self, session_id: str):
        """Update last activity time for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = datetime.now()
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            username = self.sessions[session_id]['username']
            logger.info(f"Deleting session {session_id} for user {username}")
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        now = datetime.now()
        expired_sessions = [
            sid for sid, session in self.sessions.items() 
            if now > session['expires_at']
        ]
        
        for session_id in expired_sessions:
            logger.info(f"Cleaning up expired session {session_id}")
            del self.sessions[session_id]
    
    def get_active_sessions(self) -> List[SessionInfo]:
        """Get list of active sessions."""
        self.cleanup_expired_sessions()
        return [
            SessionInfo(
                session_id=sid,
                username=session['username'],
                created_at=session['created_at'],
                last_activity=session['last_activity'],
                expires_at=session['expires_at']
            )
            for sid, session in self.sessions.items()
        ]

# Global session manager
session_manager = SessionManager()

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Messaging Bot API",
    description="REST API for Instagram messaging automation",
    version="1.0.0"
)

# CORS middleware - Updated for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:8000",  # Local development
        "https://*.vercel.app",   # Vercel deployments
        "https://*.onrender.com", # Render deployments
        "*"  # Allow all origins for now - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class InstagramBotManager:
    def __init__(self):
        self.client = Client()
        self.is_logged_in = False
        self.username = None
        self.session_file = None
        
    async def login(self, username: str, password: str, verification_code: Optional[str] = None, challenge_url: Optional[str] = None) -> tuple[bool, Optional[ChallengeResponse]]:
        """Login to Instagram account."""
        try:
            logger.info(f"Attempting to login as {username}...")
            
            # Try to load existing session
            self.session_file = f"session_{username}.json"
            if os.path.exists(self.session_file):
                try:
                    self.client.load_settings(self.session_file)
                    self.client.login(username, password)
                    logger.info("Logged in using saved session")
                except Exception as e:
                    logger.warning(f"Failed to load saved session: {e}")
                    self.client.login(username, password)
            else:
                self.client.login(username, password)
            
            # Save session
            self.client.dump_settings(self.session_file)
            self.is_logged_in = True
            self.username = username
            
            logger.info("Successfully logged in!")
            return True, None
            
        except ChallengeRequired as e:
            logger.info(f"Challenge required: {e}")
            challenge_info = getattr(e, 'challenge_info', {})
            challenge_type = getattr(e, 'challenge_type', 'Unknown')
            
            # Extract phone number if available
            phone_number = None
            if hasattr(e, 'challenge_info') and isinstance(e.challenge_info, dict):
                phone_number = e.challenge_info.get('phone_number', None)
            
            challenge_response = ChallengeResponse(
                requires_verification=True,
                challenge_type=challenge_type,
                challenge_url=str(e) if hasattr(e, '__str__') else None,
                phone_number=phone_number,
                message=f"Instagram requires {challenge_type} verification"
            )
            
            return False, challenge_response
        except LoginRequired as e:
            logger.error("Login required. Please check your credentials.")
            raise HTTPException(status_code=401, detail="Invalid credentials. Please check your username and password.")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            error_msg = str(e)
            
            # Handle specific challenge resolver errors
            if "ChallengeResolve" in error_msg and "Unknown step_name" in error_msg:
                challenge_response = ChallengeResponse(
                    requires_verification=True,
                    challenge_type="Phone Verification",
                    challenge_url=None,
                    phone_number=None,
                    message="Instagram requires phone verification. Please complete verification on your phone and try again."
                )
                return False, challenge_response
            
            raise HTTPException(status_code=500, detail=f"Login failed: {error_msg}")
    
    async def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username."""
        try:
            user_info = self.client.user_info_by_username(username)
            return str(user_info.pk)
        except Exception as e:
            logger.error(f"Failed to get user ID for {username}: {e}")
            return None
    
    async def send_message(self, username: str, message: str) -> MessageResult:
        """Send a message to a specific user."""
        if not self.is_logged_in:
            return MessageResult(username=username, success=False, error="Not logged in")
        
        try:
            user_id = await self.get_user_id(username)
            if not user_id:
                return MessageResult(username=username, success=False, error="User not found")
            
            self.client.direct_send(message, user_ids=[user_id])
            logger.info(f"Message sent to {username}")
            return MessageResult(username=username, success=True)
            
        except Exception as e:
            error_msg = f"Failed to send message: {str(e)}"
            logger.error(f"Failed to send message to {username}: {e}")
            return MessageResult(username=username, success=False, error=error_msg)
    
    async def send_messages_batch(self, usernames: List[str], message: str, delay_range: List[int]) -> List[MessageResult]:
        """Send messages to a batch of users with delays."""
        if not self.is_logged_in:
            return [MessageResult(username=u, success=False, error="Not logged in") for u in usernames]
        
        results = []
        total_users = len(usernames)
        
        logger.info(f"Starting to send messages to {total_users} users...")
        
        for i, username in enumerate(usernames):
            logger.info(f"Processing {i+1}/{total_users}: {username}")
            
            # Send message
            result = await self.send_message(username, message)
            results.append(result)
            
            # Add delay between messages (except for the last one)
            if i < total_users - 1:
                import random
                delay = random.uniform(delay_range[0], delay_range[1])
                logger.info(f"Waiting {delay:.1f} seconds before next message...")
                await asyncio.sleep(delay)
        
        # Summary
        successful = sum(1 for r in results if r.success)
        failed = total_users - successful
        logger.info(f"Message sending completed. Success: {successful}, Failed: {failed}")
        
        return results

# Helper function to get current session
def get_current_session(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get current session from cookie or parameter."""
    if not session_id:
        return None
    return session_manager.get_session(session_id)

def get_current_bot_manager(session_id: Optional[str] = None) -> Optional[InstagramBotManager]:
    """Get bot manager for current session."""
    session = get_current_session(session_id)
    if session:
        session_manager.update_activity(session_id)
        return session['bot_manager']
    return None

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")

@app.get("/api/status", response_model=BotStatus)
async def get_bot_status(session_id: Optional[str] = Cookie(None)):
    """Get current bot status for the session."""
    session = get_current_session(session_id)
    if session:
        bot_manager = session['bot_manager']
        return BotStatus(
            is_logged_in=bot_manager.is_logged_in,
            username=bot_manager.username,
            last_activity=session['last_activity'].isoformat()
        )
    else:
        return BotStatus(is_logged_in=False)

@app.post("/api/login", response_model=BotResponse)
async def login(request: LoginRequest):
    """Login to Instagram account."""
    try:
        # Create new session for this user
        session_id = session_manager.create_session(request.username)
        session = session_manager.get_session(session_id)
        bot_manager = session['bot_manager']
        
        success, challenge = await bot_manager.login(
            request.username, 
            request.password, 
            request.verification_code,
            request.challenge_url
        )
        
        if success:
            response = BotResponse(
                success=True,
                message="Successfully logged in!",
                data={"username": request.username, "session_id": session_id}
            )
            return response
        elif challenge:
            return BotResponse(
                success=False,
                message=challenge.message,
                challenge=challenge
            )
        else:
            # Remove session if login failed
            session_manager.delete_session(session_id)
            return BotResponse(
                success=False,
                message="Login failed"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logout", response_model=BotResponse)
async def logout(session_id: Optional[str] = Cookie(None)):
    """Logout from Instagram account."""
    session = get_current_session(session_id)
    if session:
        bot_manager = session['bot_manager']
        bot_manager.is_logged_in = False
        bot_manager.username = None
        
        # Delete the session
        session_manager.delete_session(session_id)
        
        return BotResponse(
            success=True,
            message="Successfully logged out!"
        )
    else:
        return BotResponse(
            success=False,
            message="No active session found"
        )

@app.post("/api/send-messages", response_model=BotResponse)
async def send_messages(request: MessageRequest, background_tasks: BackgroundTasks, session_id: Optional[str] = Cookie(None)):
    """Send messages to a list of usernames."""
    bot_manager = get_current_bot_manager(session_id)
    if not bot_manager or not bot_manager.is_logged_in:
        raise HTTPException(status_code=401, detail="Not logged in. Please login first.")
    
    if not request.usernames:
        raise HTTPException(status_code=400, detail="No usernames provided")
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Send messages in background
        results = await bot_manager.send_messages_batch(
            request.usernames,
            request.message,
            request.delay_range
        )
        
        # Save results to file with session info
        session = get_current_session(session_id)
        username = session['username'] if session else "unknown"
        
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "session_id": session_id,
            "message": request.message,
            "total_users": len(request.usernames),
            "results": [{"username": r.username, "success": r.success, "error": r.error} for r in results]
        }
        
        # Save with username prefix to avoid conflicts
        results_filename = f"message_results_{username}_{int(time.time())}.json"
        with open(results_filename, "w") as f:
            json.dump(results_data, f, indent=2)
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return BotResponse(
            success=True,
            message=f"Messages sent! Success: {successful}, Failed: {failed}",
            data={
                "total": len(request.usernames),
                "successful": successful,
                "failed": failed,
                "results": results,
                "results_file": results_filename
            }
        )
        
    except Exception as e:
        logger.error(f"Error sending messages: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending messages: {str(e)}")

@app.get("/api/results")
async def get_results(session_id: Optional[str] = Cookie(None)):
    """Get latest message results for the current session."""
    session = get_current_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="No active session")
    
    username = session['username']
    
    try:
        # Look for results files for this user
        import glob
        result_files = glob.glob(f"message_results_{username}_*.json")
        
        if result_files:
            # Get the most recent file
            latest_file = max(result_files, key=os.path.getctime)
            with open(latest_file, "r") as f:
                return json.load(f)
        else:
            return {"message": "No results found for your session"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading results: {str(e)}")

@app.post("/api/upload-usernames", response_model=BotResponse)
async def upload_usernames(request: Request):
    """Upload usernames from text content."""
    try:
        body = await request.json()
        usernames_text = body.get("usernames", "")
        
        if not usernames_text.strip():
            raise HTTPException(status_code=400, detail="No usernames provided")
        
        # Parse usernames (one per line, ignore empty lines and comments)
        usernames = [
            line.strip() 
            for line in usernames_text.split('\n') 
            if line.strip() and not line.strip().startswith('#')
        ]
        
        if not usernames:
            raise HTTPException(status_code=400, detail="No valid usernames found")
        
        # Save to file
        with open("usernames.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(usernames))
        
        return BotResponse(
            success=True,
            message=f"Successfully uploaded {len(usernames)} usernames",
            data={"count": len(usernames), "usernames": usernames}
        )
        
    except Exception as e:
        logger.error(f"Error uploading usernames: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading usernames: {str(e)}")

@app.get("/api/sessions")
async def get_active_sessions():
    """Get list of active sessions (admin endpoint)."""
    sessions = session_manager.get_active_sessions()
    return {
        "active_sessions": len(sessions),
        "sessions": [session.dict() for session in sessions]
    }

@app.post("/api/cleanup-sessions")
async def cleanup_sessions():
    """Clean up expired sessions (admin endpoint)."""
    session_manager.cleanup_expired_sessions()
    return {"message": "Sessions cleaned up successfully"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
