# Instagram Messaging Bot with Web Frontend

A modern web application for sending automated messages to a list of Instagram usernames. Features a beautiful, responsive web interface built with FastAPI backend and vanilla JavaScript frontend.

## ⚠️ Important Disclaimer

**This bot is for educational purposes only. Using automated tools on Instagram may violate their Terms of Service and could result in account restrictions or bans. Use at your own risk and always comply with Instagram's policies.**

## Features

### 🌐 Web Interface
- **Modern, Responsive UI** - Beautiful web interface that works on desktop and mobile
- **Real-time Status** - Live bot status and connection indicators
- **Progress Tracking** - Real-time progress bars and status updates
- **Results Dashboard** - Detailed success/failure reporting
- **Toast Notifications** - User-friendly feedback messages

### 🤖 Bot Functionality
- Send messages to multiple Instagram users from a list
- Configurable message content and delays
- Session management (saves login sessions)
- Detailed logging and result tracking
- Random delays between messages to appear more natural
- REST API for easy integration

### 🔐 Authentication
- Instagram credentials login
- Session persistence
- Secure password handling
- Facebook/Google OAuth (coming soon)

## What You Need

### Free Requirements:
1. **Python 3.7+** - Free
2. **Instagram Account** - Free
3. **Internet Connection** - Free
4. **Python Libraries** - All free (instagrapi, requests, cryptography)

### Cost Breakdown:
- **Python Libraries**: 100% FREE
- **Instagram Account**: FREE
- **Bot Development**: FREE (this code)
- **Total Cost**: $0

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd insta-bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the web application**
   ```bash
   python backend.py
   ```

4. **Open your browser**
   - Navigate to `http://localhost:8000`
   - The web interface will load automatically

## Quick Start

### 🌐 Web Interface (Recommended)

1. **Start the server:**
   ```bash
   python backend.py
   ```

2. **Open your browser:**
   - Go to `http://localhost:8000`
   - You'll see the beautiful web interface

3. **Login:**
   - Enter your Instagram username and password
   - Click "Login" button

4. **Send messages:**
   - Enter your message in the text area
   - Add usernames (one per line) in the usernames field
   - Configure delay settings
   - Click "Send Messages"

### 💻 Command Line Interface

#### Method 1: Using the Configuration Bot
```bash
python config_bot.py
```

#### Method 2: Using the Direct Script
```bash
python instagram_bot.py
```

#### Method 3: Using the Simple Runner
```bash
python run_bot.py
```

## Web Interface Features

### 🎨 User Interface
- **Modern Design** - Clean, Instagram-inspired interface
- **Responsive Layout** - Works perfectly on desktop, tablet, and mobile
- **Real-time Updates** - Live status indicators and progress tracking
- **Interactive Elements** - Smooth animations and hover effects

### 🔧 Functionality
- **Login System** - Secure Instagram credentials authentication
- **Message Editor** - Rich text area with character counting
- **Username Management** - Easy bulk username input and management
- **Progress Tracking** - Real-time progress bars and status updates
- **Results Dashboard** - Detailed success/failure reporting with error messages
- **Settings Panel** - Configurable delay settings and preferences

### 📱 Mobile Support
- **Touch-Friendly** - Optimized for touch devices
- **Responsive Design** - Adapts to any screen size
- **Mobile Navigation** - Easy-to-use mobile interface

## API Endpoints

The FastAPI backend provides the following REST endpoints:

- `GET /` - Serve the web interface
- `GET /api/status` - Get bot status
- `POST /api/login` - Login to Instagram
- `POST /api/logout` - Logout from Instagram
- `POST /api/send-messages` - Send messages to users
- `POST /api/upload-usernames` - Upload usernames list
- `GET /api/results` - Get message results
- `GET /api/health` - Health check

## Configuration Options

### config.json Settings (for CLI usage):

```json
{
  "instagram": {
    "username": "your_username",
    "password": "your_password"
  },
  "message": {
    "text": "Your message here",
    "delay_range": [30, 60]
  },
  "files": {
    "usernames_file": "usernames.txt",
    "results_file": "message_results.json",
    "session_file": "session_{username}.json"
  },
  "settings": {
    "max_retries": 3,
    "log_level": "INFO"
  }
}
```

## Safety Features

1. **Random Delays**: 30-60 seconds between messages (configurable)
2. **Session Management**: Saves login sessions to avoid repeated logins
3. **Error Handling**: Comprehensive error handling and logging
4. **Rate Limiting**: Built-in delays to avoid triggering Instagram's anti-bot measures

## Files Created

- `instagram_bot.log` - Detailed execution logs
- `message_results.json` - Results of message sending
- `session_username.json` - Saved login session

## Troubleshooting

### Common Issues:

1. **Login Failed**
   - Check your username and password
   - Ensure 2FA is disabled or handle it manually
   - Try logging in manually on Instagram first

2. **Challenge Required**
   - Instagram may require verification
   - Complete the challenge manually on Instagram
   - Try again after some time

3. **User Not Found**
   - Verify usernames are correct
   - Check if accounts are private or blocked

4. **Rate Limiting**
   - Increase delay between messages
   - Reduce the number of messages per session
   - Take breaks between bot sessions

## Legal and Ethical Considerations

- **Instagram Terms of Service**: Automated interactions may violate ToS
- **Account Safety**: Use responsibly to avoid account restrictions
- **Spam Prevention**: Don't send unsolicited messages
- **Rate Limits**: Respect Instagram's rate limits
- **Personal Use**: Only use with accounts you have permission to message

## Alternative Approaches

### Official Instagram API (Free but Limited)
- Instagram Graph API (requires app approval)
- Instagram Basic Display API
- More complex setup but fully compliant

### Third-Party Services (Paid)
- Instavision.io: $39/month for 100,000 requests
- LinkDM: $19/month for 25,000 DMs
- Various other services with different pricing

## Support

If you encounter issues:
1. Check the logs in `instagram_bot.log`
2. Verify your configuration
3. Ensure Instagram account is in good standing
4. Try reducing the frequency of messages

## License

This project is for educational purposes. Use responsibly and in compliance with Instagram's Terms of Service.

---

**Remember**: Always use automation tools responsibly and in accordance with platform terms of service. The developers are not responsible for any account restrictions or violations that may occur from using this bot.
