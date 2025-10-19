// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
let currentUser = null;
let authToken = null;
let chatHistory = [];

// DOM Elements
const loadingScreen = document.getElementById('loading-screen');
const authScreen = document.getElementById('auth-screen');
const chatScreen = document.getElementById('chat-screen');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const loginFormElement = document.getElementById('loginForm');
const registerFormElement = document.getElementById('registerForm');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const logoutBtn = document.getElementById('logoutBtn');
const historyBtn = document.getElementById('historyBtn');
const sidebar = document.getElementById('sidebar');
const closeSidebar = document.getElementById('closeSidebar');
const historyList = document.getElementById('historyList');
const chatMessages = document.getElementById('chat-messages');
const welcomeMessage = document.getElementById('welcome-message');
const messageInput = document.getElementById('messageInput');
const imageInput = document.getElementById('imageInput');
const sendBtn = document.getElementById('sendBtn');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeImageBtn = document.getElementById('removeImage');
const notification = document.getElementById('notification');
const notificationIcon = document.getElementById('notificationIcon');
const notificationText = document.getElementById('notificationText');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Check for existing auth token
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        
        // Verify token is still valid
        try {
            await fetchUserInfo();
            showChatScreen();
            await loadChatHistory();
        } catch (error) {
            console.error('Token validation failed:', error);
            clearAuth();
            showAuthScreen();
        }
    } else {
        showAuthScreen();
    }
    
    hideLoadingScreen();
}

// Authentication Functions
function showAuthScreen() {
    authScreen.classList.remove('hidden');
    chatScreen.classList.add('hidden');
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
}

function showChatScreen() {
    authScreen.classList.add('hidden');
    chatScreen.classList.remove('hidden');
    welcomeMessage.classList.remove('hidden');
    chatMessages.innerHTML = '';
}

function hideLoadingScreen() {
    loadingScreen.classList.add('hidden');
}

// Form Event Listeners
showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
});

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
});

loginFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleLogin();
});

registerFormElement.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleRegister();
});

logoutBtn.addEventListener('click', () => {
    clearAuth();
    showAuthScreen();
});

// Authentication Handlers
async function handleLogin() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        showNotification('Signing in...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/api/auth/login/json`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        
        // Get user info
        await fetchUserInfo();
        
        // Save to localStorage
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        showNotification('Successfully signed in!', 'success');
        showChatScreen();
        await loadChatHistory();
        
    } catch (error) {
        console.error('Login error:', error);
        showNotification(error.message, 'error');
    }
}

async function handleRegister() {
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        showNotification('Creating account...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }
        
        showNotification('Account created successfully! Please sign in.', 'success');
        
        // Switch to login form
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        
        // Pre-fill email
        document.getElementById('loginEmail').value = email;
        
    } catch (error) {
        console.error('Registration error:', error);
        showNotification(error.message, 'error');
    }
}

async function fetchUserInfo() {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
            'Authorization': `Bearer ${authToken}`,
        },
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch user info');
    }
    
    currentUser = await response.json();
}

function clearAuth() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    chatHistory = [];
}

// Chat Functions
async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/ai/history`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        if (response.ok) {
            chatHistory = await response.json();
            updateHistoryList();
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

function updateHistoryList() {
    historyList.innerHTML = '';
    
    if (chatHistory.length === 0) {
        historyList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No chat history yet</p>';
        return;
    }
    
    chatHistory.forEach((message, index) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.innerHTML = `
            <h4>${message.message.substring(0, 50)}${message.message.length > 50 ? '...' : ''}</h4>
            <p>${message.response.substring(0, 100)}${message.response.length > 100 ? '...' : ''}</p>
            <div class="date">${new Date(message.created_at).toLocaleDateString()}</div>
        `;
        
        historyItem.addEventListener('click', () => {
            loadHistoryMessage(message);
            sidebar.classList.add('hidden');
        });
        
        historyList.appendChild(historyItem);
    });
}

function loadHistoryMessage(message) {
    welcomeMessage.classList.add('hidden');
    chatMessages.innerHTML = '';
    
    // Add user message
    addMessage(message.message, 'user');
    
    // Add assistant response
    addMessage(message.response, 'assistant');
}

// Message Handling
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            imagePreview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
});

removeImageBtn.addEventListener('click', () => {
    imageInput.value = '';
    imagePreview.classList.add('hidden');
    previewImg.src = '';
});

async function sendMessage() {
    const message = messageInput.value.trim();
    const imageFile = imageInput.files[0];
    
    if (!message && !imageFile) {
        showNotification('Please enter a message or upload an image', 'warning');
        return;
    }
    
    if (!imageFile) {
        showNotification('Please upload a skin image for analysis', 'warning');
        return;
    }
    
    try {
        // Hide welcome message
        welcomeMessage.classList.add('hidden');
        
        // Add user message to chat
        addMessage(message || 'Image uploaded for analysis', 'user', imageFile);
        
        // Clear input
        messageInput.value = '';
        imageInput.value = '';
        imagePreview.classList.add('hidden');
        previewImg.src = '';
        
        // Disable send button
        sendBtn.disabled = true;
        
        // Add loading message
        const loadingMessage = addMessage('Analyzing your skin image...', 'assistant', null, true);
        
        // Prepare form data
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('symptoms', message || 'No specific symptoms described');
        
        // Send request
        const response = await fetch(`${API_BASE_URL}/api/ai/skin-analysis`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
            body: formData,
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }
        
        const result = await response.json();
        
        // Remove loading message
        loadingMessage.remove();
        
        // Add AI response
        addMessage(result.response, 'assistant');
        
        // Update chat history
        chatHistory.unshift(result);
        updateHistoryList();
        
        showNotification('Analysis completed!', 'success');
        
    } catch (error) {
        console.error('Send message error:', error);
        showNotification(error.message, 'error');
        
        // Remove loading message if it exists
        const loadingMsg = document.querySelector('.message.loading');
        if (loadingMsg) {
            loadingMsg.remove();
        }
    } finally {
        sendBtn.disabled = false;
    }
}

function addMessage(text, sender, imageFile = null, isLoading = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}${isLoading ? ' loading' : ''}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    
    content.appendChild(textDiv);
    
    // Add image if provided
    if (imageFile && sender === 'user') {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'message-image';
            content.insertBefore(img, textDiv);
        };
        reader.readAsDataURL(imageFile);
    }
    
    // Add timestamp
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString();
    content.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Sidebar Functions
historyBtn.addEventListener('click', () => {
    sidebar.classList.remove('hidden');
});

closeSidebar.addEventListener('click', () => {
    sidebar.classList.add('hidden');
});

// Notification System
function showNotification(message, type = 'info') {
    notificationText.textContent = message;
    notification.className = `notification ${type}`;
    
    // Set icon based on type
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notificationIcon.className = icons[type] || icons.info;
    
    notification.classList.remove('hidden');
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}

// Error Handling
window.addEventListener('error', (error) => {
    console.error('Global error:', error);
    showNotification('An unexpected error occurred', 'error');
});

// Network Error Handling
window.addEventListener('online', () => {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    showNotification('Connection lost', 'warning');
});
