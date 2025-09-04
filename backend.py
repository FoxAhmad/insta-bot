#!/usr/bin/env python3
"""
FastAPI Backend for Instagram Messaging Bot
Provides REST API endpoints for the web frontend.
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
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

class BotResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# Global bot instance
bot_instance = None
bot_status = BotStatus(is_logged_in=False)

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
        
    async def login(self, username: str, password: str) -> bool:
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
            
            # Update global status
            global bot_status
            bot_status.is_logged_in = True
            bot_status.username = username
            bot_status.last_activity = datetime.now().isoformat()
            
            logger.info("Successfully logged in!")
            return True
            
        except ChallengeRequired as e:
            logger.error("Challenge required. Please check your Instagram account for verification.")
            raise HTTPException(status_code=400, detail="Challenge required. Please verify your account on Instagram.")
        except LoginRequired as e:
            logger.error("Login required. Please check your credentials.")
            raise HTTPException(status_code=401, detail="Invalid credentials. Please check your username and password.")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
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

# Initialize bot manager
bot_manager = InstagramBotManager()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")

@app.get("/api/status", response_model=BotStatus)
async def get_bot_status():
    """Get current bot status."""
    return bot_status

@app.post("/api/login", response_model=BotResponse)
async def login(request: LoginRequest):
    """Login to Instagram account."""
    try:
        success = await bot_manager.login(request.username, request.password)
        if success:
            return BotResponse(
                success=True,
                message="Successfully logged in!",
                data={"username": request.username}
            )
        else:
            return BotResponse(
                success=False,
                message="Login failed"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logout", response_model=BotResponse)
async def logout():
    """Logout from Instagram account."""
    global bot_status
    bot_manager.is_logged_in = False
    bot_manager.username = None
    bot_status.is_logged_in = False
    bot_status.username = None
    bot_status.last_activity = None
    
    return BotResponse(
        success=True,
        message="Successfully logged out!"
    )

@app.post("/api/send-messages", response_model=BotResponse)
async def send_messages(request: MessageRequest, background_tasks: BackgroundTasks):
    """Send messages to a list of usernames."""
    if not bot_manager.is_logged_in:
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
        
        # Save results to file
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "message": request.message,
            "total_users": len(request.usernames),
            "results": [{"username": r.username, "success": r.success, "error": r.error} for r in results]
        }
        
        with open("message_results.json", "w") as f:
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
                "results": results
            }
        )
        
    except Exception as e:
        logger.error(f"Error sending messages: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending messages: {str(e)}")

@app.get("/api/results")
async def get_results():
    """Get latest message results."""
    try:
        if os.path.exists("message_results.json"):
            with open("message_results.json", "r") as f:
                return json.load(f)
        else:
            return {"message": "No results found"}
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
