# Multi-User Instagram Bot

## Overview

This Instagram Bot has been upgraded to support multiple concurrent users. Each user can now log in with their own Instagram credentials and send messages independently without interfering with other users.

## Key Changes

### 1. Session Management
- **Session-based Architecture**: Each user gets a unique session ID when they log in
- **Session Isolation**: Users can only access their own data and bot instances
- **Session Expiry**: Sessions automatically expire after 1 hour of inactivity
- **Session Cleanup**: Expired sessions are automatically removed

### 2. Backend Changes (`backend.py`)

#### New Components:
- `SessionManager` class: Manages all user sessions
- `SessionInfo` model: Pydantic model for session information
- Session helper functions: `get_current_session()`, `get_current_bot_manager()`

#### Modified Endpoints:
- **`/api/login`**: Now returns a session ID and creates a new bot instance per user
- **`/api/status`**: Now requires session ID to return user-specific status
- **`/api/logout`**: Now deletes the specific user's session
- **`/api/send-messages`**: Now uses the user's specific bot instance
- **`/api/results`**: Now returns results specific to the user's session

#### New Endpoints:
- **`/api/sessions`**: Admin endpoint to view all active sessions
- **`/api/cleanup-sessions`**: Admin endpoint to manually clean up expired sessions

### 3. Frontend Changes (`script.js`)

#### Session Handling:
- **Session Storage**: Session IDs are stored in localStorage
- **Session Persistence**: Users remain logged in across browser sessions
- **Session Validation**: Frontend checks session validity on page load
- **Cookie Support**: Session IDs are sent as cookies for API requests

#### Updated Functions:
- `checkBotStatus()`: Now checks for saved session ID and validates it
- `handleLogin()`: Now stores session ID from login response
- `handleLogout()`: Now clears session ID from localStorage
- All API calls now include session credentials

## How It Works

### 1. User Login Flow
```
1. User enters credentials → Frontend sends login request
2. Backend creates new session → Returns session ID
3. Frontend stores session ID → User is logged in
4. Each user gets their own bot instance
```

### 2. Session Management
```
1. Session created with unique ID (UUID)
2. Session contains: username, bot instance, timestamps
3. Session expires after 1 hour of inactivity
4. Expired sessions are automatically cleaned up
```

### 3. Message Sending
```
1. User sends message request with session ID
2. Backend finds user's bot instance using session ID
3. Bot instance sends messages using user's Instagram account
4. Results are saved with user-specific filename
```

## Security Features

### 1. Session Isolation
- Users can only access their own sessions
- No cross-user data leakage
- Session IDs are unique and unpredictable

### 2. Session Expiry
- Sessions expire after 1 hour of inactivity
- Automatic cleanup prevents session buildup
- Manual cleanup endpoint for admin use

### 3. Data Separation
- Each user's results are saved in separate files
- Session files are user-specific
- No shared state between users

## Usage Examples

### Multiple Users Login Simultaneously
```javascript
// User 1 logs in
const user1Response = await fetch('/api/login', {
    method: 'POST',
    body: JSON.stringify({username: 'user1', password: 'pass1'})
});
const user1Session = user1Response.data.session_id;

// User 2 logs in (doesn't affect user 1)
const user2Response = await fetch('/api/login', {
    method: 'POST', 
    body: JSON.stringify({username: 'user2', password: 'pass2'})
});
const user2Session = user2Response.data.session_id;
```

### Send Messages from Different Users
```javascript
// User 1 sends messages
await fetch('/api/send-messages', {
    method: 'POST',
    headers: {'Cookie': `session_id=${user1Session}`},
    body: JSON.stringify({usernames: ['target1'], message: 'Hello from user1'})
});

// User 2 sends messages (independent of user 1)
await fetch('/api/send-messages', {
    method: 'POST',
    headers: {'Cookie': `session_id=${user2Session}`},
    body: JSON.stringify({usernames: ['target2'], message: 'Hello from user2'})
});
```

## Testing

### Test Script
Run the test script to verify multi-user functionality:
```bash
python test_multi_user.py
```

### Test Scenarios
1. **Multiple Login**: Multiple users can login simultaneously
2. **Session Isolation**: Users can only access their own data
3. **Independent Messaging**: Users can send messages independently
4. **Session Cleanup**: Sessions are properly cleaned up on logout
5. **Session Expiry**: Expired sessions are automatically removed

## Configuration

### Session Timeout
Default session timeout is 1 hour (3600 seconds). To change:
```python
# In backend.py, SessionManager.__init__()
self.session_timeout = 3600  # Change to desired seconds
```

### Session Storage
Sessions are stored in memory by default. For production, consider:
- Database storage for persistence
- Redis for distributed sessions
- Session encryption for security

## Deployment Notes

### Production Considerations
1. **Session Storage**: Use Redis or database for session persistence
2. **Load Balancing**: Ensure session affinity or shared session storage
3. **Security**: Add session encryption and HTTPS
4. **Monitoring**: Monitor session usage and cleanup
5. **Rate Limiting**: Implement per-user rate limiting

### Environment Variables
```bash
# Session timeout (seconds)
SESSION_TIMEOUT=3600

# Session storage backend
SESSION_STORAGE=memory  # or 'redis' or 'database'
```

## Troubleshooting

### Common Issues

1. **Session Not Found**
   - Check if session ID is being sent correctly
   - Verify session hasn't expired
   - Ensure session cleanup hasn't removed it

2. **Multiple Users Interfering**
   - Verify each user has their own session ID
   - Check that bot instances are separate
   - Ensure session isolation is working

3. **Session Expiry Issues**
   - Check session timeout configuration
   - Verify session cleanup is running
   - Monitor session activity timestamps

### Debug Endpoints
- `GET /api/sessions`: View all active sessions
- `POST /api/cleanup-sessions`: Manually clean up sessions
- `GET /api/health`: Check server health

## Migration from Single-User

### Backward Compatibility
- Existing single-user deployments will need to update
- Frontend needs to handle session IDs
- Session management is now required

### Migration Steps
1. Update backend code
2. Update frontend code
3. Test with multiple users
4. Deploy with session management
5. Monitor session usage

## Benefits

### For Users
- **Privacy**: Each user's data is isolated
- **Independence**: Users can operate simultaneously
- **Persistence**: Login state persists across browser sessions
- **Security**: No cross-user data access

### For Administrators
- **Scalability**: Support multiple concurrent users
- **Monitoring**: Track active sessions and usage
- **Management**: Clean up expired sessions
- **Security**: Better session isolation and management

## Future Enhancements

### Planned Features
1. **Session Persistence**: Database/Redis storage
2. **User Management**: User registration and profiles
3. **Rate Limiting**: Per-user rate limits
4. **Analytics**: Session and usage analytics
5. **Admin Panel**: Session management interface

### Possible Improvements
1. **Session Sharing**: Allow session sharing between devices
2. **Session Refresh**: Automatic session refresh
3. **Multi-Device**: Support multiple devices per user
4. **Session History**: Track session activity history
