// Global state
let isLoggedIn = false;
let currentUser = null;
let messageProgress = {
    current: 0,
    total: 0,
    isRunning: false
};

// DOM elements
const loginSection = document.getElementById('loginSection');
const dashboardSection = document.getElementById('dashboardSection');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const loginForm = document.getElementById('loginForm');
const logoutBtn = document.getElementById('logoutBtn');
const messageText = document.getElementById('messageText');
const charCount = document.getElementById('charCount');
const usernamesInput = document.getElementById('usernamesInput');
const loadUsernamesBtn = document.getElementById('loadUsernamesBtn');
const sendMessagesBtn = document.getElementById('sendMessagesBtn');
const progressCard = document.getElementById('progressCard');
const resultsCard = document.getElementById('resultsCard');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkBotStatus();
});

// Initialize the application
function initializeApp() {
    // Set up character counter for message text
    messageText.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
    
    // Enable/disable send button based on input
    usernamesInput.addEventListener('input', function() {
        const hasUsernames = this.value.trim().split('\n').filter(u => u.trim()).length > 0;
        const hasMessage = messageText.value.trim().length > 0;
        sendMessagesBtn.disabled = !(hasUsernames && hasMessage && isLoggedIn);
    });
    
    messageText.addEventListener('input', function() {
        const hasUsernames = usernamesInput.value.trim().split('\n').filter(u => u.trim()).length > 0;
        const hasMessage = this.value.trim().length > 0;
        sendMessagesBtn.disabled = !(hasUsernames && hasMessage && isLoggedIn);
    });
}

// Set up event listeners
function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);
    
    // Logout button
    logoutBtn.addEventListener('click', handleLogout);
    
    // Load usernames button
    loadUsernamesBtn.addEventListener('click', handleLoadUsernames);
    
    // Send messages button
    sendMessagesBtn.addEventListener('click', handleSendMessages);
    
    // Social login buttons (placeholder)
    document.getElementById('facebookLogin').addEventListener('click', function() {
        showToast('Facebook login coming soon!', 'info');
    });
    
    document.getElementById('googleLogin').addEventListener('click', function() {
        showToast('Google login coming soon!', 'info');
    });
}

// Check bot status on page load
async function checkBotStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        if (status.is_logged_in) {
            isLoggedIn = true;
            currentUser = status.username;
            showDashboard();
            updateStatusIndicator(true);
        } else {
            showLogin();
            updateStatusIndicator(false);
        }
    } catch (error) {
        console.error('Error checking bot status:', error);
        updateStatusIndicator(false);
    }
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showToast('Please enter both username and password', 'error');
        return;
    }
    
    showLoading('Logging in...');
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            isLoggedIn = true;
            currentUser = username;
            showDashboard();
            updateStatusIndicator(true);
            showToast('Successfully logged in!', 'success');
        } else {
            showToast(result.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Handle logout
async function handleLogout() {
    showLoading('Logging out...');
    
    try {
        const response = await fetch('/api/logout', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        isLoggedIn = false;
        currentUser = null;
        showLogin();
        updateStatusIndicator(false);
        resetDashboard();
        showToast('Successfully logged out!', 'success');
    } catch (error) {
        console.error('Logout error:', error);
        showToast('Logout failed', 'error');
    } finally {
        hideLoading();
    }
}

// Handle load usernames
async function handleLoadUsernames() {
    const usernames = usernamesInput.value.trim();
    
    if (!usernames) {
        showToast('Please enter some usernames', 'error');
        return;
    }
    
    showLoading('Loading usernames...');
    
    try {
        const response = await fetch('/api/upload-usernames', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ usernames })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`Successfully loaded ${result.data.count} usernames`, 'success');
            // Enable send button if message is also present
            const hasMessage = messageText.value.trim().length > 0;
            sendMessagesBtn.disabled = !(hasMessage && isLoggedIn);
        } else {
            showToast(result.message || 'Failed to load usernames', 'error');
        }
    } catch (error) {
        console.error('Load usernames error:', error);
        showToast('Failed to load usernames', 'error');
    } finally {
        hideLoading();
    }
}

// Handle send messages
async function handleSendMessages() {
    const usernames = usernamesInput.value.trim().split('\n').filter(u => u.trim());
    const message = messageText.value.trim();
    const delayMin = parseInt(document.getElementById('delayMin').value) || 30;
    const delayMax = parseInt(document.getElementById('delayMax').value) || 60;
    
    if (!usernames.length) {
        showToast('Please enter some usernames', 'error');
        return;
    }
    
    if (!message) {
        showToast('Please enter a message', 'error');
        return;
    }
    
    // Confirm before sending
    if (!confirm(`Are you sure you want to send this message to ${usernames.length} users?\n\nMessage: "${message}"`)) {
        return;
    }
    
    showLoading('Sending messages...');
    showProgress();
    
    try {
        const response = await fetch('/api/send-messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                usernames,
                message,
                delay_range: [delayMin, delayMax]
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(`Messages sent! Success: ${result.data.successful}, Failed: ${result.data.failed}`, 'success');
            showResults(result.data.results);
        } else {
            showToast(result.message || 'Failed to send messages', 'error');
        }
    } catch (error) {
        console.error('Send messages error:', error);
        showToast('Failed to send messages', 'error');
    } finally {
        hideLoading();
        hideProgress();
    }
}

// Show dashboard
function showDashboard() {
    loginSection.style.display = 'none';
    dashboardSection.style.display = 'block';
    document.getElementById('loggedInUser').textContent = `@${currentUser}`;
}

// Show login
function showLogin() {
    loginSection.style.display = 'block';
    dashboardSection.style.display = 'none';
}

// Update status indicator
function updateStatusIndicator(online) {
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('#statusText');
    
    if (online) {
        statusDot.classList.remove('offline');
        statusDot.classList.add('online');
        statusText.textContent = 'Online';
    } else {
        statusDot.classList.remove('online');
        statusDot.classList.add('offline');
        statusText.textContent = 'Offline';
    }
}

// Reset dashboard
function resetDashboard() {
    messageText.value = '';
    usernamesInput.value = '';
    charCount.textContent = '0';
    sendMessagesBtn.disabled = true;
    hideProgress();
    hideResults();
}

// Show progress
function showProgress() {
    progressCard.style.display = 'block';
    messageProgress.isRunning = true;
    updateProgress(0, 0);
}

// Hide progress
function hideProgress() {
    progressCard.style.display = 'none';
    messageProgress.isRunning = false;
}

// Update progress
function updateProgress(current, total) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressPercent = document.getElementById('progressPercent');
    
    messageProgress.current = current;
    messageProgress.total = total;
    
    const percentage = total > 0 ? (current / total) * 100 : 0;
    
    progressFill.style.width = `${percentage}%`;
    progressText.textContent = `${current} / ${total}`;
    progressPercent.textContent = `${Math.round(percentage)}%`;
}

// Show results
function showResults(results) {
    resultsCard.style.display = 'block';
    
    const successCount = results.filter(r => r.success).length;
    const errorCount = results.filter(r => !r.success).length;
    
    document.getElementById('successCount').textContent = successCount;
    document.getElementById('errorCount').textContent = errorCount;
    
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.success ? 'success' : 'error'}`;
        
        resultItem.innerHTML = `
            <span>@${result.username}</span>
            <span>
                <i class="fas ${result.success ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                ${result.success ? 'Success' : result.error || 'Failed'}
            </span>
        `;
        
        resultsList.appendChild(resultItem);
    });
}

// Hide results
function hideResults() {
    resultsCard.style.display = 'none';
}

// Show loading overlay
function showLoading(text = 'Loading...') {
    document.getElementById('loadingText').textContent = text;
    loadingOverlay.classList.add('show');
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.classList.remove('show');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Utility functions
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showToast('An unexpected error occurred', 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('An unexpected error occurred', 'error');
});
