/**
 * SUMMONERS REUNION - CHAT FUNCTIONALITY
 * Handles chat logic, SSE streaming, and message management
 */

// Configuration
// API URL can be set via window.API_BASE_URL (for deployment) or defaults to localhost
const CONFIG = {
    apiBaseUrl: window.API_BASE_URL || 'http://localhost:8000',
    endpoints: {
        health: '/api/health',
        chatStream: '/api/chat/stream',
        chat: '/api/chat'
    },
    checkHealthInterval: 30000, // 30 seconds
    reconnectDelay: 3000, // 3 seconds
};

// State management
class ChatState {
    constructor() {
        this.conversationHistory = [];
        this.isStreaming = false;
        this.currentStreamingMessage = null;
        this.eventSource = null;
        this.isHealthy = false;
    }

    addMessage(role, content, timestamp = new Date()) {
        const message = {
            role,
            content,
            timestamp: timestamp.toISOString()
        };
        this.conversationHistory.push(message);
        return message;
    }

    clearHistory() {
        this.conversationHistory = [];
    }

    getHistory() {
        return this.conversationHistory.slice(); // Return a copy
    }
}

// Initialize state
const state = new ChatState();

// DOM Elements
const elements = {
    messagesContainer: document.getElementById('messages'),
    messagesWrapper: document.getElementById('messagesWrapper'),
    messageInput: document.getElementById('messageInput'),
    sendButton: document.getElementById('sendButton'),
    clearButton: document.getElementById('clearButton'),
    typingIndicator: document.getElementById('typingIndicator'),
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    errorToast: document.getElementById('errorToast'),
    errorMessage: document.getElementById('errorMessage'),
    welcomeTime: document.getElementById('welcomeTime'),
    suggestionsButton: document.getElementById('suggestionsButton'),
    suggestionsPanel: document.getElementById('suggestionsPanel'),
    closeSuggestions: document.getElementById('closeSuggestions')
};

/**
 * Initialize the chat application
 */
function initializeChat() {
    console.log('Initializing Summoners Reunion AI Chat...');

    // Set welcome message time
    if (elements.welcomeTime) {
        elements.welcomeTime.textContent = formatTime(new Date());
    }

    // Event listeners
    elements.sendButton.addEventListener('click', handleSendMessage);
    elements.clearButton.addEventListener('click', handleClearChat);

    // Debug: Check if suggestions elements exist
    console.log('Suggestions button:', elements.suggestionsButton);
    console.log('Suggestions panel:', elements.suggestionsPanel);
    console.log('Close button:', elements.closeSuggestions);

    if (elements.suggestionsButton) {
        elements.suggestionsButton.addEventListener('click', toggleSuggestions);
        console.log('Suggestions button listener added');
    } else {
        console.error('Suggestions button not found!');
    }

    if (elements.closeSuggestions) {
        elements.closeSuggestions.addEventListener('click', closeSuggestionsPanel);
    }

    // Add click handlers for suggestion items
    const suggestionItems = document.querySelectorAll('.suggestion-item');
    console.log('Found suggestion items:', suggestionItems.length);
    suggestionItems.forEach(item => {
        item.addEventListener('click', handleSuggestionClick);
    });

    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Auto-resize textarea
    elements.messageInput.addEventListener('input', autoResizeTextarea);

    // Check backend health
    checkHealth();
    setInterval(checkHealth, CONFIG.checkHealthInterval);

    console.log('Chat initialized successfully');
}

/**
 * Check backend health status
 */
async function checkHealth() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.endpoints.health}`);
        const data = await response.json();

        const isHealthy = data.bedrock_configured && data.status === 'healthy';
        updateStatus(isHealthy);
        state.isHealthy = isHealthy;

    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus(false);
        state.isHealthy = false;
    }
}

/**
 * Update status indicator
 */
function updateStatus(isOnline) {
    if (isOnline) {
        elements.statusDot.classList.add('online');
        elements.statusText.textContent = 'Online';
    } else {
        elements.statusDot.classList.remove('online');
        elements.statusText.textContent = 'Offline';
    }
}

/**
 * Handle send message
 */
async function handleSendMessage() {
    const message = elements.messageInput.value.trim();

    if (!message) {
        return;
    }

    if (state.isStreaming) {
        showError('Please wait for the current response to complete');
        return;
    }

    if (!state.isHealthy) {
        showError('Backend is offline. Please check your connection.');
        return;
    }

    // Clear input
    elements.messageInput.value = '';
    autoResizeTextarea();

    // Add user message to conversation
    const userMessage = state.addMessage('user', message);
    displayUserMessage(userMessage);

    // Scroll to bottom
    scrollToBottom();

    // Show typing indicator
    showTypingIndicator();

    // Send message and stream response
    console.log("there")
    await streamChatResponse(message);
}

/**
 * Display user message in chat
 */
function displayUserMessage(message) {
    const messageElement = createMessageElement('user', message.content, new Date(message.timestamp));
    elements.messagesContainer.appendChild(messageElement);
}

/**
 * Display assistant message in chat
 */
function displayAssistantMessage(content, timestamp) {
    const messageElement = createMessageElement('assistant', content, timestamp);
    elements.messagesContainer.appendChild(messageElement);
    return messageElement;
}

/**
 * Create message element
 */
function createMessageElement(role, content, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = `message-avatar ${role}-avatar`;

    if (role === 'assistant') {
        avatar.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
        `;
    } else {
        avatar.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
                <path d="M6.5 18.5C7 16 9 14 12 14C15 14 17 16 17.5 18.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
        `;
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const header = document.createElement('div');
    header.className = 'message-header';

    const sender = document.createElement('span');
    sender.className = 'message-sender';
    sender.textContent = role === 'assistant' ? 'AI Agent' : 'You';

    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = formatTime(timestamp);

    header.appendChild(sender);
    header.appendChild(time);

    const text = document.createElement('div');
    text.className = 'message-text';
    text.innerHTML = formatMessageContent(content);

    contentDiv.appendChild(header);
    contentDiv.appendChild(text);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
}

/**
 * Format message content (supports basic markdown-like formatting)
 */
function formatMessageContent(content) {
    return content
        .split('\n')
        .map(line => line.trim() ? `<p>${escapeHtml(line)}</p>` : '')
        .join('');
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Stream chat response using SSE
 */
async function streamChatResponse(message) {
    state.isStreaming = true;
    let streamedContent = '';
    const startTime = new Date();
    console.log("here")

    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}${CONFIG.endpoints.chatStream}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_history: state.getHistory(),
                use_knowledge_base: true
            })
        });
        console.log(response)

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        // Hide typing indicator
        hideTypingIndicator();

        // Create message element for streaming
        let messageElement = null;
        let textElement = null;

        while (true) {
            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.substring(6);

                    if (data.trim() === '') continue;

                    try {
                        const parsed = JSON.parse(data);

                        if (parsed.done) {
                            // Streaming complete
                            continue;
                        }

                        if (parsed.content) {
                            streamedContent += parsed.content;

                            // Create message element if it doesn't exist
                            if (!messageElement) {
                                messageElement = displayAssistantMessage(streamedContent, startTime);
                                textElement = messageElement.querySelector('.message-text');
                            } else {
                                // Update existing message
                                textElement.innerHTML = formatMessageContent(streamedContent);
                            }

                            // Auto scroll
                            scrollToBottom();
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e);
                    }
                }
            }
        }

        // Add to conversation history
        state.addMessage('assistant', streamedContent, startTime);

    } catch (error) {
        console.error('Error streaming response:', error);
        hideTypingIndicator();
        showError(`Failed to get response: ${error.message}`);

        // Display error message
        displayAssistantMessage(
            'Sorry, I encountered an error. Please try again.',
            new Date()
        );
    } finally {
        state.isStreaming = false;
    }
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    elements.typingIndicator.style.display = 'flex';
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    elements.typingIndicator.style.display = 'none';
}

/**
 * Handle clear chat
 */
function handleClearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        // Clear conversation history
        state.clearHistory();

        // Remove all messages except welcome message
        const messages = elements.messagesContainer.querySelectorAll('.message:not(.welcome-message)');
        messages.forEach(msg => msg.remove());

        // Focus on input
        elements.messageInput.focus();
    }
}

/**
 * Toggle suggestions panel
 */
function toggleSuggestions() {
    console.log('Toggle suggestions clicked');
    console.log('Panel element:', elements.suggestionsPanel);
    console.log('Current display:', elements.suggestionsPanel?.style.display);

    if (!elements.suggestionsPanel) {
        console.error('Suggestions panel not found!');
        return;
    }

    const isVisible = elements.suggestionsPanel.style.display === 'block';
    if (isVisible) {
        closeSuggestionsPanel();
    } else {
        openSuggestionsPanel();
    }
}

/**
 * Open suggestions panel
 */
function openSuggestionsPanel() {
    console.log('Opening suggestions panel');
    if (elements.suggestionsPanel && elements.suggestionsButton) {
        elements.suggestionsPanel.style.display = 'block';
        elements.suggestionsButton.classList.add('active');
        console.log('Panel opened, display set to:', elements.suggestionsPanel.style.display);
    }
}

/**
 * Close suggestions panel
 */
function closeSuggestionsPanel() {
    console.log('Closing suggestions panel');
    if (elements.suggestionsPanel && elements.suggestionsButton) {
        elements.suggestionsPanel.style.display = 'none';
        elements.suggestionsButton.classList.remove('active');
    }
}

/**
 * Handle suggestion click
 */
function handleSuggestionClick(event) {
    const suggestionText = event.currentTarget.dataset.suggestion;

    // Set the input value
    elements.messageInput.value = suggestionText;

    // Close suggestions panel
    closeSuggestionsPanel();

    // Auto-resize textarea
    autoResizeTextarea();

    // Focus on input
    elements.messageInput.focus();
}

/**
 * Show error toast
 */
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.style.display = 'block';

    setTimeout(() => {
        elements.errorToast.style.display = 'none';
    }, 5000);
}

/**
 * Format time to HH:MM
 */
function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Auto resize textarea
 */
function autoResizeTextarea() {
    elements.messageInput.style.height = 'auto';
    elements.messageInput.style.height = elements.messageInput.scrollHeight + 'px';
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
    setTimeout(() => {
        elements.messagesWrapper.scrollTop = elements.messagesWrapper.scrollHeight;
    }, 100);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChat);
} else {
    initializeChat();
}
