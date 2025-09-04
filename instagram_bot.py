#!/usr/bin/env python3
"""
Instagram Messaging Bot
A Python agent for sending messages to a list of Instagram usernames.
"""

import time
import random
import json
import os
from typing import List, Dict, Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, SelectContactPointRecoveryForm
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstagramMessagingBot:
    def __init__(self, username: str, password: str):
        """
        Initialize the Instagram messaging bot.
        
        Args:
            username (str): Instagram username
            password (str): Instagram password
        """
        self.client = Client()
        self.username = username
        self.password = password
        self.is_logged_in = False
        
    def login(self) -> bool:
        """
        Login to Instagram account.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info(f"Attempting to login as {self.username}...")
            
            # Try to load existing session
            session_file = f"session_{self.username}.json"
            if os.path.exists(session_file):
                try:
                    self.client.load_settings(session_file)
                    self.client.login(self.username, self.password)
                    logger.info("Logged in using saved session")
                except Exception as e:
                    logger.warning(f"Failed to load saved session: {e}")
                    # Try fresh login
                    self.client.login(self.username, self.password)
            else:
                # Fresh login
                self.client.login(self.username, self.password)
            
            # Save session for future use
            self.client.dump_settings(session_file)
            self.is_logged_in = True
            logger.info("Successfully logged in!")
            return True
            
        except ChallengeRequired as e:
            logger.error("Challenge required. Please check your Instagram account for verification.")
            logger.error("You may need to complete 2FA or solve a captcha.")
            return False
        except LoginRequired as e:
            logger.error("Login required. Please check your credentials.")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def get_user_id(self, username: str) -> Optional[str]:
        """
        Get user ID from username.
        
        Args:
            username (str): Instagram username
            
        Returns:
            Optional[str]: User ID if found, None otherwise
        """
        try:
            user_info = self.client.user_info_by_username(username)
            return str(user_info.pk)
        except Exception as e:
            logger.error(f"Failed to get user ID for {username}: {e}")
            return None
    
    def send_message(self, username: str, message: str) -> bool:
        """
        Send a message to a specific user.
        
        Args:
            username (str): Target username
            message (str): Message to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.is_logged_in:
            logger.error("Not logged in. Please login first.")
            return False
        
        try:
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                logger.error(f"Could not find user: {username}")
                return False
            
            # Send message
            self.client.direct_send(message, user_ids=[user_id])
            logger.info(f"Message sent to {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {username}: {e}")
            return False
    
    def send_messages_to_list(self, usernames: List[str], message: str, 
                            delay_range: tuple = (30, 60)) -> Dict[str, bool]:
        """
        Send messages to a list of usernames.
        
        Args:
            usernames (List[str]): List of usernames to message
            message (str): Message to send
            delay_range (tuple): Random delay range in seconds between messages
            
        Returns:
            Dict[str, bool]: Results for each username
        """
        if not self.is_logged_in:
            logger.error("Not logged in. Please login first.")
            return {}
        
        results = {}
        total_users = len(usernames)
        
        logger.info(f"Starting to send messages to {total_users} users...")
        
        for i, username in enumerate(usernames, 1):
            logger.info(f"Processing {i}/{total_users}: {username}")
            
            # Send message
            success = self.send_message(username, message)
            results[username] = success
            
            # Add delay between messages (except for the last one)
            if i < total_users:
                delay = random.uniform(delay_range[0], delay_range[1])
                logger.info(f"Waiting {delay:.1f} seconds before next message...")
                time.sleep(delay)
        
        # Summary
        successful = sum(results.values())
        failed = total_users - successful
        logger.info(f"Message sending completed. Success: {successful}, Failed: {failed}")
        
        return results
    
    def load_usernames_from_file(self, filename: str) -> List[str]:
        """
        Load usernames from a text file (one username per line).
        
        Args:
            filename (str): Path to the file containing usernames
            
        Returns:
            List[str]: List of usernames
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f.readlines() if line.strip()]
            logger.info(f"Loaded {len(usernames)} usernames from {filename}")
            return usernames
        except Exception as e:
            logger.error(f"Failed to load usernames from {filename}: {e}")
            return []
    
    def save_results(self, results: Dict[str, bool], filename: str = "message_results.json"):
        """
        Save message results to a JSON file.
        
        Args:
            results (Dict[str, bool]): Results dictionary
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """Main function to run the Instagram messaging bot."""
    
    # Configuration
    USERNAME = "your_instagram_username"  # Replace with your Instagram username
    PASSWORD = "your_instagram_password"  # Replace with your Instagram password
    MESSAGE = "Hello! This is an automated message from my bot. Hope you're doing well! 😊"
    USERNAMES_FILE = "usernames.txt"  # File containing usernames (one per line)
    
    # Alternative: Use a list directly
    # usernames = ["username1", "username2", "username3"]
    
    # Initialize bot
    bot = InstagramMessagingBot(USERNAME, PASSWORD)
    
    # Login
    if not bot.login():
        logger.error("Failed to login. Exiting.")
        return
    
    # Load usernames
    usernames = bot.load_usernames_from_file(USERNAMES_FILE)
    if not usernames:
        logger.error("No usernames loaded. Please check your usernames file.")
        return
    
    # Send messages
    logger.info(f"Sending message to {len(usernames)} users...")
    logger.info(f"Message: {MESSAGE}")
    
    results = bot.send_messages_to_list(
        usernames=usernames,
        message=MESSAGE,
        delay_range=(30, 60)  # Random delay between 30-60 seconds
    )
    
    # Save results
    bot.save_results(results)
    
    logger.info("Bot execution completed!")

if __name__ == "__main__":
    main()
