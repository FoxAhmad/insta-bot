#!/usr/bin/env python3
"""
Configuration-based Instagram Bot
A more flexible version that uses config.json for settings.
"""

import json
import time
import random
import logging
from typing import List, Dict, Optional
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired

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

class ConfigInstagramBot:
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the bot with configuration from JSON file.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config = self.load_config(config_file)
        self.client = Client()
        self.is_logged_in = False
        
    def load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def login(self) -> bool:
        """Login to Instagram using config credentials."""
        try:
            username = self.config.get('instagram', {}).get('username')
            password = self.config.get('instagram', {}).get('password')
            
            if not username or not password:
                logger.error("Username or password not found in config")
                return False
            
            logger.info(f"Attempting to login as {username}...")
            
            # Try to load existing session
            session_file = f"session_{username}.json"
            if os.path.exists(session_file):
                try:
                    self.client.load_settings(session_file)
                    self.client.login(username, password)
                    logger.info("Logged in using saved session")
                except Exception as e:
                    logger.warning(f"Failed to load saved session: {e}")
                    self.client.login(username, password)
            else:
                self.client.login(username, password)
            
            # Save session
            self.client.dump_settings(session_file)
            self.is_logged_in = True
            logger.info("Successfully logged in!")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Get user ID from username."""
        try:
            user_info = self.client.user_info_by_username(username)
            return str(user_info.pk)
        except Exception as e:
            logger.error(f"Failed to get user ID for {username}: {e}")
            return None
    
    def send_message(self, username: str, message: str) -> bool:
        """Send a message to a specific user."""
        if not self.is_logged_in:
            logger.error("Not logged in. Please login first.")
            return False
        
        try:
            user_id = self.get_user_id(username)
            if not user_id:
                logger.error(f"Could not find user: {username}")
                return False
            
            self.client.direct_send(message, user_ids=[user_id])
            logger.info(f"Message sent to {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {username}: {e}")
            return False
    
    def load_usernames_from_file(self, filename: str) -> List[str]:
        """Load usernames from file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                usernames = [line.strip() for line in f.readlines() 
                           if line.strip() and not line.startswith('#')]
            logger.info(f"Loaded {len(usernames)} usernames from {filename}")
            return usernames
        except Exception as e:
            logger.error(f"Failed to load usernames from {filename}: {e}")
            return []
    
    def send_messages_to_list(self, usernames: List[str]) -> Dict[str, bool]:
        """Send messages to a list of usernames using config settings."""
        if not self.is_logged_in:
            logger.error("Not logged in. Please login first.")
            return {}
        
        message = self.config.get('message', {}).get('text', 'Hello!')
        delay_range = self.config.get('message', {}).get('delay_range', [30, 60])
        
        results = {}
        total_users = len(usernames)
        
        logger.info(f"Starting to send messages to {total_users} users...")
        logger.info(f"Message: {message}")
        
        for i, username in enumerate(usernames, 1):
            logger.info(f"Processing {i}/{total_users}: {username}")
            
            success = self.send_message(username, message)
            results[username] = success
            
            # Add delay between messages
            if i < total_users:
                delay = random.uniform(delay_range[0], delay_range[1])
                logger.info(f"Waiting {delay:.1f} seconds before next message...")
                time.sleep(delay)
        
        # Summary
        successful = sum(results.values())
        failed = total_users - successful
        logger.info(f"Message sending completed. Success: {successful}, Failed: {failed}")
        
        return results
    
    def save_results(self, results: Dict[str, bool]):
        """Save results to file specified in config."""
        results_file = self.config.get('files', {}).get('results_file', 'message_results.json')
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {results_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """Main function using configuration file."""
    bot = ConfigInstagramBot("config.json")
    
    # Login
    if not bot.login():
        logger.error("Failed to login. Exiting.")
        return
    
    # Load usernames
    usernames_file = bot.config.get('files', {}).get('usernames_file', 'usernames.txt')
    usernames = bot.load_usernames_from_file(usernames_file)
    
    if not usernames:
        logger.error("No usernames loaded. Please check your usernames file.")
        return
    
    # Send messages
    results = bot.send_messages_to_list(usernames)
    
    # Save results
    bot.save_results(results)
    
    logger.info("Bot execution completed!")

if __name__ == "__main__":
    main()
