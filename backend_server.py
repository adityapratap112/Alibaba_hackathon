#!/usr/bin/env python3
"""
🔧 Backend Server - Trading Engine API
Runs on port 5001 with detailed logging
"""

import os
import sys
import json
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - BACKEND - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import trading components
try:
    from frontend_ode import AlibabaAI
    from crypto_trading_engine import TradingEngine, TradeCommandParser
    TRADING_AVAILABLE = True
    logger.info("✅ Trading engine imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import trading engine: {e}")
    TRADING_AVAILABLE = False

app = Flask(__name__)

# Simple CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Store chatbot sessions
sessions = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Enhanced health check with detailed status"""
    logger.info("🔍 Health check requested")
    
    health_data = {
        'success': True,
        'message': 'Backend Trading API is running',
        'version': '2.1.0',
        'trading_available': TRADING_AVAILABLE,
        'active_sessions': len(sessions),
        'timestamp': datetime.now().isoformat(),
        'server': 'Backend (Port 5001)'
    }
    
    logger.info(f"✅ Health check: {len(sessions)} active sessions, trading: {TRADING_AVAILABLE}")
    return jsonify(health_data)

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new trading session with enhanced logging"""
    try:
        session_id = str(uuid.uuid4())
        user_id = f"user_{session_id[:8]}"
        
        logger.info(f"🔄 Creating session {session_id} for user {user_id}")
        
        if not TRADING_AVAILABLE:
            logger.error("❌ Trading engine not available")
            return jsonify({
                'success': False,
                'error': 'Trading engine not available'
            }), 500
        
        # Create chatbot instance
        chatbot = AlibabaAI(user_id=user_id)
        sessions[session_id] = {
            'chatbot': chatbot,
            'created_at': datetime.now().isoformat(),
            'message_count': 0,
            'trade_count': 0
        }
        
        # Get initial portfolio
        portfolio_result = chatbot.get_portfolio()
        
        logger.info(f"✅ Session {session_id} created successfully")
        logger.info(f"💼 Initial portfolio: ${portfolio_result.get('portfolio_value', {}).get('total_value', 0):.2f}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_id': user_id,
            'ai_status': 'ready' if chatbot.available else 'unavailable',
            'trading_available': TRADING_AVAILABLE,
            'initial_portfolio': portfolio_result if portfolio_result['success'] else None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Session creation failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to create session: {str(e)}'
        }), 500

@app.route('/api/session/<session_id>/message', methods=['POST'])
def process_message(session_id):
    """Process message with enhanced logging and trade detection"""
    try:
        if session_id not in sessions:
            logger.error(f"❌ Session {session_id} not found")
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        data = request.get_json()
        if not data or 'message' not in data:
            logger.error("❌ No message in request")
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        message = data['message']
        session = sessions[session_id]
        chatbot = session['chatbot']
        
        logger.info(f"📥 Message from {session_id[:8]}...: '{message}'")
        
        # Check if it's a trading command
        if TRADING_AVAILABLE:
            trade_parser = TradeCommandParser()
            trade_command = trade_parser.parse_trade_command(message)
            
            if trade_command:
                logger.info(f"💰 Trade command detected: {trade_command}")
                
                # Handle confirmation needed
                if trade_command.get('needs_confirmation'):
                    logger.info(f"⚠️  Trade needs confirmation: {trade_command}")
                    confirmation_text = f"🤔 **Trade Confirmation Needed**\n\n"
                    confirmation_text += f"I detected you want to **{trade_command['action']}** "
                    confirmation_text += f"**{trade_command['amount']} {trade_command['symbol']}**\n\n"
                    confirmation_text += f"Original message: \"{trade_command['original_message']}\"\n\n"
                    confirmation_text += f"To confirm, please say: \"{trade_command['action'].lower()} {trade_command['amount']} {trade_command['symbol']}\"\n"
                    confirmation_text += f"Or be more specific with your trade request."
                    
                    return jsonify({
                        'success': True,
                        'content': confirmation_text,
                        'trade_executed': False,
                        'needs_confirmation': True,
                        'suggested_command': f"{trade_command['action'].lower()} {trade_command['amount']} {trade_command['symbol']}",
                        'timestamp': datetime.now().isoformat(),
                        'session_id': session_id
                    })
        
        # Process message through chatbot
        session['message_count'] += 1
        response = chatbot.chat_response(message)
        
        # Check if trade was executed
        if response.get('trade_executed'):
            session['trade_count'] += 1
            logger.info(f"✅ Trade executed in session {session_id[:8]}... (Total trades: {session['trade_count']})")
        else:
            logger.info(f"💬 Analysis response sent to {session_id[:8]}...")
        
        response['session_id'] = session_id
        response['message_count'] = session['message_count']
        response['trade_count'] = session['trade_count']
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Message processing error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to process message: {str(e)}'
        }), 500

@app.route('/api/session/<session_id>/portfolio', methods=['GET'])
def get_portfolio(session_id):
    """Get portfolio with logging"""
    try:
        if session_id not in sessions:
            logger.error(f"❌ Portfolio request - session {session_id} not found")
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        chatbot = sessions[session_id]['chatbot']
        portfolio_result = chatbot.get_portfolio()
        
        if portfolio_result['success']:
            total_value = portfolio_result['portfolio_value']['total_value']
            logger.info(f"📊 Portfolio requested for {session_id[:8]}...: ${total_value:.2f}")
        else:
            logger.error(f"❌ Portfolio error for {session_id[:8]}...: {portfolio_result.get('error')}")
        
        portfolio_result['session_id'] = session_id
        return jsonify(portfolio_result)
        
    except Exception as e:
        logger.error(f"❌ Portfolio retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get portfolio: {str(e)}'
        }), 500

@app.route('/api/session/<session_id>/trade', methods=['POST'])
def execute_direct_trade(session_id):
    """Execute direct trade with logging"""
    try:
        if session_id not in sessions:
            logger.error(f"❌ Direct trade - session {session_id} not found")
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Trade data is required'
            }), 400
        
        required_fields = ['action', 'symbol', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        chatbot = sessions[session_id]['chatbot']
        session = sessions[session_id]
        
        logger.info(f"💰 Direct trade: {data['action']} {data['amount']} {data['symbol']} (Session: {session_id[:8]}...)")
        
        trade_result = chatbot.execute_trade(
            data['action'], 
            data['symbol'], 
            data['amount']
        )
        
        if trade_result['success']:
            session['trade_count'] += 1
            logger.info(f"✅ Direct trade executed successfully (Total trades: {session['trade_count']})")
        else:
            logger.error(f"❌ Direct trade failed: {trade_result['error']}")
        
        trade_result['session_id'] = session_id
        trade_result['trade_count'] = session['trade_count']
        
        return jsonify(trade_result)
        
    except Exception as e:
        logger.error(f"❌ Direct trade execution error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to execute trade: {str(e)}'
        }), 500

@app.route('/api/crypto/price/<symbol>', methods=['GET'])
def get_crypto_price(symbol):
    """Get crypto price with logging"""
    try:
        logger.info(f"💲 Price request for {symbol}")
        
        if TRADING_AVAILABLE:
            temp_chatbot = AlibabaAI()
            response = temp_chatbot.get_crypto_price(symbol)
            
            if response.get('success'):
                logger.info(f"✅ Price for {symbol}: ${response['current_price']:,.2f}")
            else:
                logger.error(f"❌ Price fetch failed for {symbol}: {response.get('error')}")
        else:
            response = {'success': False, 'error': 'Trading engine not available'}
            logger.error("❌ Price request failed - trading engine not available")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Price fetch error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get price: {str(e)}'
        }), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all sessions with detailed info"""
    try:
        logger.info(f"📋 Session list requested ({len(sessions)} active)")
        
        session_list = []
        for session_id, session_data in sessions.items():
            chatbot = session_data['chatbot']
            portfolio_result = chatbot.get_portfolio()
            
            session_info = {
                'session_id': session_id,
                'user_id': chatbot.user_id,
                'created_at': session_data['created_at'],
                'message_count': session_data['message_count'],
                'trade_count': session_data['trade_count'],
                'ai_status': 'ready' if chatbot.available else 'unavailable',
                'portfolio_value': portfolio_result.get('portfolio_value', {}).get('total_value', 0) if portfolio_result['success'] else 0
            }
            session_list.append(session_info)
        
        return jsonify({
            'success': True,
            'sessions': session_list,
            'total_sessions': len(sessions),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Session list error: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to list sessions: {str(e)}'
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Backend Trading Server")
    logger.info("📡 Backend API will be available at: http://localhost:5001")
    logger.info(f"💰 Trading Engine: {'✅ Available' if TRADING_AVAILABLE else '❌ Not Available'}")
    
    if TRADING_AVAILABLE:
        logger.info("📋 Available endpoints:")
        logger.info("  - POST /api/session/create - Create trading session")
        logger.info("  - POST /api/session/{id}/message - Process message")
        logger.info("  - GET /api/session/{id}/portfolio - Get portfolio")
        logger.info("  - POST /api/session/{id}/trade - Execute trade")
        logger.info("  - GET /api/crypto/price/{symbol} - Get price")
        logger.info("  - GET /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
