// JavaScript for LangChain Multi-Agent AI Interface

class ChatInterface {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.textInput = document.getElementById('textInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.voiceBtn = document.getElementById('voiceBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.statusBar = document.getElementById('statusBar');
        this.loading = document.getElementById('loading');
    }

    bindEvents() {
        // Text input events
        this.sendBtn.addEventListener('click', () => this.sendTextMessage());
        this.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendTextMessage();
            }
        });

        // Voice input events
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());

        // Clear chat
        this.clearBtn.addEventListener('click', () => this.clearChat());

        // Auto-resize text input
        this.textInput.addEventListener('input', () => this.autoResizeInput());
    }

    async sendTextMessage() {
        const message = this.textInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.textInput.value = '';
        this.showLoading(true);

        try {
            const response = await fetch('/query/text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.addMessage(result.response, 'bot', {
                    agent: result.agent_used,
                    time: result.execution_time
                });
                this.updateStatus(`Response from ${result.agent_used} in ${result.execution_time.toFixed(2)}s`);
            } else {
                this.addMessage('Sorry, I encountered an error processing your request.', 'bot');
                this.updateStatus('Error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I couldn\'t connect to the server.', 'bot');
            this.updateStatus('Connection error');
        } finally {
            this.showLoading(false);
        }
    }

    async toggleVoiceRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processRecording();
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.voiceBtn.textContent = '🛑 Stop Recording';
            this.voiceBtn.classList.add('recording');
            this.updateStatus('Recording... Click to stop');

        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.updateStatus('Microphone access denied');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.voiceBtn.textContent = '🎤 Voice Input';
            this.voiceBtn.classList.remove('recording');
            this.updateStatus('Processing audio...');
        }
    }

    async processRecording() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'recording.wav');

        this.showLoading(true);

        try {
            const response = await fetch('/query/voice', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                // Add the transcribed text as user message
                this.addMessage(result.text_query, 'user', { type: 'voice' });
                
                // Add the bot response
                this.addMessage(result.response, 'bot', {
                    agent: result.agent_used,
                    time: result.execution_time
                });

                // Play audio response if available
                if (result.audio_response) {
                    this.playAudioResponse(result.audio_response);
                }

                this.updateStatus(`Voice processed by ${result.agent_used}`);
            } else {
                this.addMessage('Sorry, I couldn\'t process your voice message.', 'bot');
                this.updateStatus('Voice processing error');
            }
        } catch (error) {
            console.error('Error processing voice:', error);
            this.addMessage('Sorry, there was an error processing your voice message.', 'bot');
            this.updateStatus('Voice processing failed');
        } finally {
            this.showLoading(false);
        }
    }

    playAudioResponse(audioBase64) {
        try {
            const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
            audio.play().catch(error => {
                console.error('Error playing audio:', error);
            });
        } catch (error) {
            console.error('Error creating audio:', error);
        }
    }

    addMessage(text, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        let messageContent = `<div class="message-text">${this.escapeHtml(text)}</div>`;
        
        if (metadata.agent || metadata.time || metadata.type) {
            let metaInfo = [];
            if (metadata.type === 'voice') metaInfo.push('🎤 Voice');
            if (metadata.agent) metaInfo.push(`Agent: ${metadata.agent}`);
            if (metadata.time) metaInfo.push(`${metadata.time.toFixed(2)}s`);
            
            messageContent += `<div class="agent-info">${metaInfo.join(' | ')}</div>`;
        }
        
        messageDiv.innerHTML = messageContent;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    clearChat() {
        this.chatMessages.innerHTML = '';
        this.updateStatus('Chat cleared');
    }

    showLoading(show) {
        this.loading.style.display = show ? 'block' : 'none';
        this.sendBtn.disabled = show;
        this.voiceBtn.disabled = show;
    }

    updateStatus(message) {
        this.statusBar.textContent = message;
        setTimeout(() => {
            this.statusBar.textContent = 'Ready';
        }, 3000);
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    autoResizeInput() {
        this.textInput.style.height = 'auto';
        this.textInput.style.height = Math.min(this.textInput.scrollHeight, 120) + 'px';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chat interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
    
    // Add welcome message
    setTimeout(() => {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message bot-message';
        welcomeDiv.innerHTML = `
            <div class="message-text">
                Welcome to the LangChain Multi-Agent AI System! 🤖<br><br>
                I have specialized agents ready to help you with:
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>🌤️ Weather information and forecasts</li>
                    <li>📰 Latest news and research</li>
                    <li>🧮 Calculations and general assistance</li>
                </ul>
                You can type your question or use voice input. How can I help you today?
            </div>
            <div class="agent-info">System | Multi-Agent Coordinator</div>
        `;
        chatMessages.appendChild(welcomeDiv);
    }, 500);
});
