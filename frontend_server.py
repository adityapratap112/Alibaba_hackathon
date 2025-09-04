#!/usr/bin/env python3
"""
🖥️ Frontend Server - Crypto Trading Chatbot
Runs on port 3000 with detailed logging
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - FRONTEND - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import our chatbot
try:
    from frontend_ode import AlibabaAI
    from crypto_trading_engine import TradeCommandParser
    CHATBOT_AVAILABLE = True
    logger.info("✅ Chatbot modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import chatbot: {e}")
    CHATBOT_AVAILABLE = False

app = Flask(__name__)

# Backend API URL
BACKEND_URL = "http://localhost:5001"

# Store chatbot sessions
sessions = {}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def frontend_dashboard():
    """Frontend dashboard with enhanced logging"""
    logger.info("📱 Frontend dashboard accessed")
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Crypto Trading Frontend</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { background: #1a73e8; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .servers { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
            .server-status { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .chat-container { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .messages { height: 400px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; background: #fafafa; }
            .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
            .user-message { background: #e3f2fd; text-align: right; }
            .bot-message { background: #f1f8e9; }
            .trade-success { background: #e8f5e8; border-left: 4px solid #4caf50; }
            .trade-error { background: #ffebee; border-left: 4px solid #f44336; }
            .system-message { background: #fff3e0; border-left: 4px solid #ff9800; font-size: 12px; }
            .input-area { display: flex; gap: 10px; }
            input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 12px 20px; background: #1a73e8; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #1557b0; }
            .status-good { color: #4caf50; }
            .status-bad { color: #f44336; }
            .logs { background: #263238; color: #fff; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Crypto Trading Frontend</h1>
                <p>Frontend Server - Enhanced Logging & Debugging</p>
            </div>
            
            <div class="servers">
                <div class="server-status">
                    <h3>🖥️ Frontend Server</h3>
                    <p>Port: <strong>3000</strong></p>
                    <p>Status: <span class="status-good">✅ Running</span></p>
                    <p>Logs: <span id="frontendLogs">0</span> entries</p>
                </div>
                
                <div class="server-status">
                    <h3>🔧 Backend API</h3>
                    <p>Port: <strong>5001</strong></p>
                    <p>Status: <span id="backendStatus">🔄 Checking...</span></p>
                    <p>Trading: <span id="tradingStatus">🔄 Checking...</span></p>
                </div>
            </div>
            
            <div class="chat-container">
                <h3>💬 AI Trading Chat</h3>
                <div id="messages" class="messages"></div>
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Try: 'buy 0.01 BTC', 'show portfolio', 'what's Bitcoin doing?'" />
                    <button onclick="sendMessage()">Send</button>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4>📊 Frontend Logs</h4>
                    <div id="frontendLogDisplay" class="logs">Frontend server started...\n</div>
                </div>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            let logCount = 0;
            
            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                checkBackendStatus();
                createSession();
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
                
                // Update logs periodically
                setInterval(updateLogs, 2000);
            });
            
            // Check backend status
            async function checkBackendStatus() {
                try {
                    const response = await fetch('/api/backend-status');
                    const data = await response.json();
                    
                    document.getElementById('backendStatus').innerHTML = 
                        data.backend_available ? '<span class="status-good">✅ Connected</span>' : '<span class="status-bad">❌ Offline</span>';
                    document.getElementById('tradingStatus').innerHTML = 
                        data.trading_available ? '<span class="status-good">✅ Ready</span>' : '<span class="status-bad">❌ Unavailable</span>';
                        
                } catch (error) {
                    document.getElementById('backendStatus').innerHTML = '<span class="status-bad">❌ Error</span>';
                    document.getElementById('tradingStatus').innerHTML = '<span class="status-bad">❌ Error</span>';
                }
            }
            
            // Create session
            async function createSession() {
                try {
                    addSystemMessage('🔄 Creating trading session...');
                    const response = await fetch('/api/session/create', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        sessionId = data.session_id;
                        addSystemMessage(`✅ Session created: ${sessionId.substring(0, 8)}...`);
                        addMessage('🤖 Trading session ready! You can now trade and ask questions.', 'bot-message');
                    } else {
                        addSystemMessage(`❌ Session failed: ${data.error}`);
                    }
                } catch (error) {
                    addSystemMessage(`❌ Connection error: ${error.message}`);
                }
            }
            
            // Send message
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message || !sessionId) return;
                
                addMessage(message, 'user-message');
                addSystemMessage(`📤 Sending: "${message}"`);
                input.value = '';
                
                try {
                    const response = await fetch('/api/session/message', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            session_id: sessionId,
                            message: message 
                        })
                    });
                    
                    const data = await response.json();
                    addSystemMessage(`📥 Response received (${data.success ? 'success' : 'error'})`);
                    
                    if (data.success) {
                        const messageClass = data.trade_executed ? 'trade-success' : 'bot-message';
                        addMessage(data.content, messageClass);
                        
                        if (data.trade_executed) {
                            addSystemMessage('💰 Trade executed - portfolio updated');
                        }
                    } else {
                        addMessage('❌ Error: ' + data.error, 'trade-error');
                        addSystemMessage(`❌ Error: ${data.error}`);
                    }
                } catch (error) {
                    addMessage('❌ Connection error: ' + error.message, 'trade-error');
                    addSystemMessage(`❌ Network error: ${error.message}`);
                }
            }
            
            // Add message to chat
            function addMessage(content, className) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${className}`;
                messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            // Add system message
            function addSystemMessage(content) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message system-message';
                messageDiv.innerHTML = `[${new Date().toLocaleTimeString()}] ${content}`;
                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                
                // Update log display
                const logDisplay = document.getElementById('frontendLogDisplay');
                logDisplay.innerHTML += `[${new Date().toLocaleTimeString()}] ${content}\\n`;
                logDisplay.scrollTop = logDisplay.scrollHeight;
                
                logCount++;
                document.getElementById('frontendLogs').textContent = logCount;
            }
            
            // Update logs
            function updateLogs() {
                checkBackendStatus();
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/api/backend-status')
def backend_status():
    """Check backend server status"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        backend_data = response.json()
        
        logger.info("✅ Backend health check successful")
        return jsonify({
            'success': True,
            'backend_available': True,
            'trading_available': backend_data.get('trading_available', False),
            'backend_version': backend_data.get('version', 'unknown')
        })
    except Exception as e:
        logger.error(f"❌ Backend health check failed: {e}")
        return jsonify({
            'success': False,
            'backend_available': False,
            'trading_available': False,
            'error': str(e)
        })

@app.route('/api/session/create', methods=['POST'])
def create_frontend_session():
    """Create session via backend"""
    try:
        logger.info("🔄 Creating new trading session")
        
        response = requests.post(f"{BACKEND_URL}/api/session/create", timeout=10)
        data = response.json()
        
        if data.get('success'):
            logger.info(f"✅ Session created: {data['session_id']}")
        else:
            logger.error(f"❌ Session creation failed: {data.get('error')}")
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"❌ Session creation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Frontend session error: {str(e)}'
        })

@app.route('/api/session/message', methods=['POST'])
def send_frontend_message():
    """Send message via backend"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message')
        
        logger.info(f"📤 Message from session {session_id[:8]}...: '{message}'")
        
        response = requests.post(
            f"{BACKEND_URL}/api/session/{session_id}/message",
            json={'message': message},
            timeout=30
        )
        result = response.json()
        
        if result.get('success'):
            if result.get('trade_executed'):
                logger.info(f"💰 Trade executed: {message}")
            else:
                logger.info(f"💬 Analysis response sent")
        else:
            logger.error(f"❌ Message processing failed: {result.get('error')}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"❌ Message forwarding error: {e}")
        return jsonify({
            'success': False,
            'error': f'Frontend message error: {str(e)}'
        })

if __name__ == '__main__':
    logger.info("🚀 Starting Frontend Server")
    logger.info("📡 Frontend will be available at: http://localhost:3000")
    logger.info("🔗 Backend API expected at: http://localhost:5001")
    logger.info(f"🤖 Chatbot modules: {'✅ Available' if CHATBOT_AVAILABLE else '❌ Not Available'}")
    
    app.run(debug=True, host='0.0.0.0', port=3000)
