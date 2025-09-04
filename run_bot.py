#!/usr/bin/env python3
"""
Simple runner script for the Instagram bot.
This provides an easy way to run the bot with minimal setup.
"""

import os
import sys
from config_bot import ConfigInstagramBot

def main():
    """Simple runner for the Instagram bot."""
    print("🤖 Instagram Messaging Bot")
    print("=" * 40)
    
    # Check if config file exists
    if not os.path.exists("config.json"):
        print("❌ config.json not found!")
        print("Please edit config.json with your Instagram credentials first.")
        return
    
    # Check if usernames file exists
    if not os.path.exists("usernames.txt"):
        print("❌ usernames.txt not found!")
        print("Please add usernames to usernames.txt first.")
        return
    
    # Initialize and run bot
    try:
        bot = ConfigInstagramBot("config.json")
        
        print("🔐 Logging in...")
        if not bot.login():
            print("❌ Login failed. Please check your credentials in config.json")
            return
        
        print("✅ Login successful!")
        
        # Load usernames
        usernames_file = bot.config.get('files', {}).get('usernames_file', 'usernames.txt')
        usernames = bot.load_usernames_from_file(usernames_file)
        
        if not usernames:
            print("❌ No usernames found. Please add usernames to usernames.txt")
            return
        
        print(f"📝 Found {len(usernames)} usernames to message")
        
        # Confirm before sending
        message = bot.config.get('message', {}).get('text', 'Hello!')
        print(f"💬 Message: {message}")
        
        confirm = input("\n⚠️  Do you want to proceed? (y/N): ").lower().strip()
        if confirm != 'y':
            print("❌ Operation cancelled.")
            return
        
        # Send messages
        print("\n📤 Sending messages...")
        results = bot.send_messages_to_list(usernames)
        
        # Show results
        successful = sum(results.values())
        failed = len(usernames) - successful
        
        print(f"\n📊 Results:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        # Save results
        bot.save_results(results)
        print(f"💾 Results saved to message_results.json")
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check instagram_bot.log for details.")

if __name__ == "__main__":
    main()
