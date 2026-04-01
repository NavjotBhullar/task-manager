// ============================================
// CHAT APPLICATION - JavaScript
// ============================================

// Global Variables
let token = localStorage.getItem('token');
let currentUserId = localStorage.getItem('user_id');
let currentUserEmail = localStorage.getItem('email');
let ws = null;
let currentChat = null;
let allUsers = [];
let onlineUsers = [];

// ============================================
// INITIALIZATION
// ============================================

console.log('🚀 Chat App Starting...');
console.log('User ID:', currentUserId);
console.log('Email:', currentUserEmail);

// Check authentication
if (!token || !currentUserId) {
    console.error('❌ Not authenticated');
    window.location.href = '/';
}

// Display user info
document.getElementById('userEmail').textContent = currentUserEmail;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    loadUsers();
    setupEventListeners();
});

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Send button
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    
    // Enter key to send
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Close modal on background click
    document.getElementById('createGroupModal').addEventListener('click', (e) => {
        if (e.target.id === 'createGroupModal') {
            closeCreateGroupModal();
        }
    });
}

// ============================================
// WEBSOCKET
// ============================================

function connectWebSocket() {
    console.log('🔌 Connecting WebSocket...');
    updateConnectionStatus(false);
    
    const wsUrl = `ws://${window.location.host}/ws?token=${token}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket Connected');
        updateConnectionStatus(true);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 Received:', data);
        
        if (data.type === 'online_users') {
            onlineUsers = data.users;
            console.log('👥 Online users:', onlineUsers);
            displayUsers();
        } else if (data.type === 'message') {
            handleIncomingMessage(data);
        }
    };

    ws.onerror = (error) => {
        console.error('❌ WebSocket Error:', error);
        updateConnectionStatus(false);
    };

    ws.onclose = () => {
        console.log('❌ WebSocket Disconnected');
        updateConnectionStatus(false);
        
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
}

function updateConnectionStatus(connected) {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    
    if (connected) {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// ============================================
// USERS
// ============================================

async function loadUsers() {
    console.log('📡 Loading users...');
    
    try {
        const response = await fetch('/users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            allUsers = await response.json();
            console.log('✅ Users loaded:', allUsers.length);
            displayUsers();
        } else if (response.status === 401) {
            logout();
        } else {
            console.error('❌ Failed to load users');
        }
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

function displayUsers() {
    const container = document.getElementById('usersList');
    container.innerHTML = '';
    
    // Filter out current user
    const otherUsers = allUsers.filter(u => u.id !== currentUserId);
    
    if (otherUsers.length === 0) {
        container.innerHTML = `
            <div style="padding: 30px; text-align: center; color: #666;">
                No other users found
            </div>
        `;
        return;
    }
    
    // Separate online and offline users
    const online = otherUsers.filter(u => onlineUsers.includes(u.id));
    const offline = otherUsers.filter(u => !onlineUsers.includes(u.id));
    
    // Online users section
    if (online.length > 0) {
        container.innerHTML += `<div class="section-label">🟢 Online (${online.length})</div>`;
        online.forEach(user => {
            container.innerHTML += createUserItem(user, true);
        });
    }
    
    // Offline users section
    if (offline.length > 0) {
        container.innerHTML += `<div class="section-label">⚫ Offline (${offline.length})</div>`;
        offline.forEach(user => {
            container.innerHTML += createUserItem(user, false);
        });
    }
    
    // Add click handlers
    container.querySelectorAll('.list-item').forEach(item => {
        item.addEventListener('click', () => {
            const userId = item.dataset.userId;
            const userName = item.dataset.userName;
            selectChat('user', userId, userName);
        });
    });
}

async function sendImage() {
    const fileInput = document.getElementById("imageInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Select an image first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await res.json();

    const message = {
        msg_type: "image",
        file_url: data.url,
        is_group: currentChat.type === "group"
    };

    if (currentChat.type === "group") {
        message.group_id = currentChat.id;
    } else {
        message.receiver_id = currentChat.id;
    }

    ws.send(JSON.stringify(message));

    fileInput.value = "";
}

function createUserItem(user, isOnline) {
    const initials = getInitials(user.full_name);
    const isActive = currentChat && currentChat.type === 'user' && currentChat.id === user.id;
    
    return `
        <div class="list-item ${isActive ? 'active' : ''}" 
             data-user-id="${user.id}" 
             data-user-name="${user.full_name}">
            <div class="avatar">
                ${initials}
                ${isOnline ? '<div class="online-badge"></div>' : ''}
            </div>
            <div class="item-info">
                <div class="item-name">${user.full_name}</div>
                <div class="item-status">${isOnline ? 'Online' : 'Offline'}</div>
            </div>
        </div>
    `;
}

function getInitials(name) {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

// ============================================
// GROUPS
// ============================================

async function loadGroups() {
    try {
        const response = await fetch(`/groups?token=${token}`);
        if (response.ok) {
            const groups = await response.json();
            displayGroups(groups);
        }
    } catch (error) {
        console.error('❌ Error loading groups:', error);
    }
}

function displayGroups(groups) {
    const container = document.getElementById('groupsList');
    container.innerHTML = '';
    
    if (groups.length === 0) {
        container.innerHTML = `
            <div style="padding: 30px; text-align: center; color: #666;">
                No groups yet
            </div>
        `;
        return;
    }
    
    groups.forEach(group => {
        const isActive = currentChat && currentChat.type === 'group' && currentChat.id === group.id;
        
        container.innerHTML += `
            <div class="list-item ${isActive ? 'active' : ''}" 
                 data-group-id="${group.id}" 
                 data-group-name="${group.name}">
                <div class="avatar group">👥</div>
                <div class="item-info">
                    <div class="item-name">${group.name}</div>
                    <div class="item-status">${group.members.length} members</div>
                </div>
            </div>
        `;
    });
    
    // Add click handlers
    container.querySelectorAll('.list-item').forEach(item => {
        item.addEventListener('click', () => {
            const groupId = item.dataset.groupId;
            const groupName = item.dataset.groupName;
            selectChat('group', groupId, groupName);
        });
    });
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Show/hide lists
    if (tabName === 'users') {
        document.getElementById('usersList').style.display = 'block';
        document.getElementById('groupsList').style.display = 'none';
    } else {
        document.getElementById('usersList').style.display = 'none';
        document.getElementById('groupsList').style.display = 'block';
        loadGroups();
    }
}

// ============================================
// CHAT SELECTION
// ============================================

function selectChat(type, id, name) {
    console.log(`📱 Selected: ${type} - ${name} (${id})`);
    
    currentChat = { type, id, name };
    
    // Update header
    const header = document.getElementById('chatHeader');
    header.classList.add('active');
    
    document.getElementById('chatName').textContent = name;
    document.getElementById('chatAvatar').textContent = type === 'group' ? '👥' : getInitials(name);
    document.getElementById('chatAvatar').className = type === 'group' ? 'avatar group' : 'avatar';
    
    // Update status
    if (type === 'user') {
        const isOnline = onlineUsers.includes(id);
        document.getElementById('chatStatus').textContent = isOnline ? '🟢 Online' : '⚫ Offline';
    } else {
        document.getElementById('chatStatus').textContent = 'Group Chat';
    }
    
    // Enable input
    document.getElementById('messageInput').disabled = false;
    document.getElementById('sendBtn').disabled = false;
    document.getElementById('messageInput').focus();
    
    // Hide empty state
    document.getElementById('emptyState').style.display = 'none';
    
    // Update active state in list
    displayUsers();
    if (type === 'group') {
        loadGroups();
    }
    
    // Load messages
    loadHistory();
}

// ============================================
// MESSAGES
// ============================================

async function loadHistory() {
    if (!currentChat) return;
    
    console.log(`📜 Loading history for ${currentChat.type}: ${currentChat.id}`);
    
    try {
        const params = new URLSearchParams({ token });
        
        if (currentChat.type === 'group') {
            params.append('group_id', currentChat.id);
        } else {
            params.append('receiver_id', currentChat.id);
        }
        
        const response = await fetch(`/messages/history?${params}`);
        
        if (response.ok) {
            const messages = await response.json();
            console.log(`✅ Loaded ${messages.length} messages`);
            displayMessages(messages);
        }
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

function displayMessages(messages) {
    const container = document.getElementById('messagesContainer');
    container.innerHTML = '';
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-text">No messages yet. Say hello!</div>
            </div>
        `;
        return;
    }
    
    messages.forEach(msg => addMessageToUI(msg));
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function addMessageToUI(msg) {
    const container = document.getElementById('messagesContainer');
    
    // Remove empty state if present
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) {
        container.innerHTML = '';
    }
    
    const isSent = msg.sender_id === currentUserId;
    const sender = allUsers.find(u => u.id === msg.sender_id);
    const senderName = isSent ? 'You' : (sender ? sender.full_name : 'Unknown');
    
    const time = new Date(msg.timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
    
    messageDiv.innerHTML = `
        ${!isSent && currentChat && currentChat.type === 'group' ? 
            `<div class="message-sender">${senderName}</div>` : ''}
        <div class="message-bubble">${escapeHtml(msg.content)}</div>
        <div class="message-time">${time}</div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    //demo comment for now
    if (msg.msg_type === "image") {
    messageDiv.innerHTML = `
        <img src="${msg.file_url}" style="max-width:200px; border-radius:10px;" />
        <div class="message-time">${time}</div>
        `;
         } else {
    messageDiv.innerHTML = `
        ${!isSent && currentChat.type === 'group' ? `<div class="message-sender">${senderName}</div>` : ''}
        <div class="message-bubble">${escapeHtml(msg.content)}</div>
        <div class="message-time">${time}</div>
    `;
}
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleIncomingMessage(data) {
    console.log('📩 Incoming message:', data);
    
    if (!currentChat) {
        console.log('No chat selected, ignoring message');
        return;
    }
    
    // Check if message belongs to current chat
    let isRelevant = false;
    
    if (currentChat.type === 'group') {
        isRelevant = data.group_id === currentChat.id;
    } else {
        isRelevant = (data.sender_id === currentChat.id) || 
                     (data.receiver_id === currentChat.id && data.sender_id === currentUserId);
    }
    
    console.log('Is relevant to current chat:', isRelevant);
    
    if (isRelevant) {
        addMessageToUI(data);
    }
}

// ============================================
// SEND MESSAGE
// ============================================

// function sendMessage() {
//     const input = document.getElementById('messageInput');
//     const content = input.value.trim();
    
//     if (!content) {
//         console.log('❌ Empty message');
//         return;
//     }
    
//     if (!currentChat) {
//         console.log('❌ No chat selected');
//         alert('Please select a user or group first');
//         return;
//     }
    
//     if (!ws || ws.readyState !== WebSocket.OPEN) {
//         console.error('❌ WebSocket not connected');
//         alert('Connection lost. Please refresh the page.');
//         return;
//     }
    
//     const message = {
//         content: content,
//         is_group: currentChat.type === 'group'
//     };
    
//     if (currentChat.type === 'group') {
//     isRelevant = data.is_group === true && data.group_id === currentChat.id;
//       } else {
//        isRelevant = data.is_group === false &&
//         (
//             (data.sender_id === currentChat.id) ||
//             (data.receiver_id === currentChat.id && data.sender_id === currentUserId)
//         );
//     }
    
//     console.log('📤 Sending:', message);
//     ws.send(JSON.stringify(message));
    
//     // Clear input
//     input.value = '';
//     input.focus();
// }

function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();

    if (!content || !currentChat) return;

    const message = {
        content: content,
        msg_type: "text",
        is_group: currentChat.type === 'group'
    };

    if (currentChat.type === 'group') {
        message.group_id = currentChat.id;
    } else {
        message.receiver_id = currentChat.id;
    }

    ws.send(JSON.stringify(message));

    input.value = '';
}

// ============================================
// GROUP MODAL
// ============================================

function openCreateGroupModal() {
    document.getElementById('createGroupModal').classList.add('active');
    
    const membersList = document.getElementById('membersList');
    membersList.innerHTML = '';
    
    const otherUsers = allUsers.filter(u => u.id !== currentUserId);
    
    if (otherUsers.length === 0) {
        membersList.innerHTML = '<div style="padding: 15px; color: #888;">No users available</div>';
        return;
    }
    
    otherUsers.forEach(user => {
        membersList.innerHTML += `
            <div class="member-item">
                <input type="checkbox" id="member_${user.id}" value="${user.id}">
                <label for="member_${user.id}">${user.full_name}</label>
            </div>
        `;
    });
}

function closeCreateGroupModal() {
    document.getElementById('createGroupModal').classList.remove('active');
    document.getElementById('groupNameInput').value = '';
}

async function createGroup() {
    const name = document.getElementById('groupNameInput').value.trim();
    const checkboxes = document.querySelectorAll('#membersList input:checked');
    const members = Array.from(checkboxes).map(cb => cb.value);
    
    if (!name) {
        alert('Please enter a group name');
        return;
    }
    
    if (members.length === 0) {
        alert('Please select at least one member');
        return;
    }
    
    try {
        const response = await fetch(`/groups?token=${token}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, members })
        });
        
        if (response.ok) {
            closeCreateGroupModal();
            switchTab('groups');
            alert('✅ Group created!');
        } else {
            alert('❌ Failed to create group');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        alert('❌ Error creating group');
    }
}

// ============================================
// LOGOUT
// ============================================

function logout() {
    localStorage.clear();
    if (ws) ws.close();
    window.location.href = '/';
}