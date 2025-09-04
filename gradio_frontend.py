#!/usr/bin/env python3
"""
🌐 Gradio Frontend for Alibaba AI Crypto Chatbot
Runs on port 3000, connects to backend at port 8000
"""

import os
import sys
import json
import logging
import gradio as gr
import requests
from datetime import datetime
from typing import Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - FRONTEND:3000 - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('frontend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("=" * 60)
logger.info("🌐 GRADIO FRONTEND STARTING UP")
logger.info(f"📅 Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"🐍 Python Version: {sys.version}")
logger.info(f"📂 Working Directory: {os.getcwd()}")
logger.info("=" * 60)

# Import the AlibabaAI class from frontend_ode
try:
    from frontend_ode import AlibabaAI, TRADING_AVAILABLE
    logger.info("✅ AlibabaAI imported successfully from frontend_ode.py")
except ImportError as e:
    logger.error(f"❌ Failed to import AlibabaAI: {e}")
    AlibabaAI = None
    TRADING_AVAILABLE = False

# Backend API URL
BACKEND_URL = "http://localhost:8000"

# Global variables for session management
current_session = None
chat_history = []

def initialize_session():
    """Initialize a new AlibabaAI session"""
    global current_session, chat_history

    try:
        logger.info("🔄 Initializing new AlibabaAI session")

        if AlibabaAI is None:
            return "❌ AlibabaAI not available"

        # Create unique user ID
        user_id = f"gradio_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        current_session = AlibabaAI(user_id=user_id)
        chat_history = []

        if current_session.available:
            status_msg = f"✅ Session initialized successfully!\n👤 User ID: {user_id}\n💰 Trading: {'✅ Available' if TRADING_AVAILABLE else '❌ Not Available'}"
            logger.info(f"✅ Session created for user: {user_id}")

            # Get initial portfolio if trading is available
            if TRADING_AVAILABLE:
                portfolio_result = current_session.get_portfolio()
                if portfolio_result.get('success'):
                    portfolio_value = portfolio_result['portfolio_value']['total_value']
                    status_msg += f"\n💼 Initial Portfolio Value: ${portfolio_value:,.2f}"

            return status_msg
        else:
            return "❌ Session failed to initialize - check API key"

    except Exception as e:
        logger.error(f"❌ Session initialization error: {e}")
        return f"❌ Error: {str(e)}"

def chat_with_ai(message: str, history):
    """Handle chat messages with the AI"""
    global current_session, chat_history

    if not message.strip():
        return history, ""

    if current_session is None:
        history.append([message, "❌ No active session. Please initialize first."])
        return history, ""

    try:
        logger.info(f"📥 User message: '{message}'")

        # Add user message to chat history
        chat_history.append({"role": "user", "message": message, "timestamp": datetime.now().isoformat()})

        # Prepare context data
        context_data = {
            'chat_history': chat_history[-3:] if len(chat_history) > 3 else chat_history
        }

        # Get AI response
        response = current_session.chat_response(message, context_data)

        if response.get('success'):
            ai_message = response['content']

            # Add AI response to chat history
            chat_history.append({"role": "assistant", "message": ai_message, "timestamp": datetime.now().isoformat()})

            # Check if it was a trade
            if response.get('trade_executed'):
                logger.info("💰 Trade executed successfully")
                ai_message += "\n\n✅ **Trade executed successfully!**"
            else:
                logger.info("💬 Analysis response provided")

            history.append([message, ai_message])
            return history, ""
        else:
            error_msg = f"❌ Error: {response.get('error', 'Unknown error')}"
            logger.error(f"❌ AI response error: {response.get('error')}")
            history.append([message, error_msg])
            return history, ""

    except Exception as e:
        error_msg = f"❌ Chat error: {str(e)}"
        logger.error(f"❌ Chat error: {e}")
        history.append([message, error_msg])
        return history, ""

def get_portfolio_info() -> str:
    """Get current portfolio information"""
    global current_session
    
    if current_session is None:
        return "❌ No active session. Please initialize first."
    
    if not TRADING_AVAILABLE:
        return "❌ Trading not available"
    
    try:
        logger.info("📊 Portfolio request")
        portfolio_result = current_session.get_portfolio()
        
        if portfolio_result.get('success'):
            portfolio = portfolio_result['portfolio']
            portfolio_value = portfolio_result['portfolio_value']
            
            info = f"💼 **Portfolio Summary**\n\n"
            info += f"**Cash Balance:** ${portfolio['cash_balance']:,.2f}\n"
            info += f"**Crypto Value:** ${portfolio_value['crypto_value']:,.2f}\n"
            info += f"**Total Value:** ${portfolio_value['total_value']:,.2f}\n\n"
            
            if portfolio['holdings']:
                info += "**Holdings:**\n"
                for symbol, details in portfolio_value['holdings_detail'].items():
                    info += f"• {symbol}: {details['amount']:.6f} (${details['value']:,.2f})\n"
            else:
                info += "**Holdings:** None (100% cash)\n"
            
            info += f"\n**Total Transactions:** {portfolio['transaction_count']}"
            info += f"\n**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            logger.info(f"📊 Portfolio value: ${portfolio_value['total_value']:,.2f}")
            return info
        else:
            error_msg = f"❌ Portfolio error: {portfolio_result.get('error')}"
            logger.error(f"❌ Portfolio error: {portfolio_result.get('error')}")
            return error_msg
            
    except Exception as e:
        error_msg = f"❌ Portfolio fetch error: {str(e)}"
        logger.error(f"❌ Portfolio fetch error: {e}")
        return error_msg

def get_crypto_price(symbol: str) -> str:
    """Get current crypto price"""
    global current_session
    
    if not symbol.strip():
        return "Please enter a crypto symbol (e.g., BTC, ETH, SOL)"
    
    if current_session is None:
        return "❌ No active session. Please initialize first."
    
    try:
        logger.info(f"💲 Price request for {symbol}")
        price_result = current_session.get_crypto_price(symbol.strip())
        
        if price_result.get('success'):
            info = f"💰 **{price_result['symbol']} Price Info**\n\n"
            info += f"**Current Price:** ${price_result['current_price']:,.2f}\n"
            info += f"**24h Change:** {price_result['price_change_24h']:+.2f}%\n"
            
            if 'high_24h' in price_result:
                info += f"**24h High:** ${price_result['high_24h']:,.2f}\n"
                info += f"**24h Low:** ${price_result['low_24h']:,.2f}\n"
            
            if 'volume_24h' in price_result:
                info += f"**24h Volume:** ${price_result['volume_24h']:,.0f}\n"
            
            info += f"**Source:** {price_result.get('source', 'Unknown')}\n"
            info += f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            logger.info(f"💲 {symbol} price: ${price_result['current_price']:,.2f}")
            return info
        else:
            error_msg = f"❌ Price error: {price_result.get('error')}"
            logger.error(f"❌ Price error for {symbol}: {price_result.get('error')}")
            return error_msg
            
    except Exception as e:
        error_msg = f"❌ Price fetch error: {str(e)}"
        logger.error(f"❌ Price fetch error for {symbol}: {e}")
        return error_msg

def check_backend_health() -> str:
    """Check backend server health"""
    try:
        logger.info("🔍 Checking backend health")
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                info = f"✅ **Backend Status: Healthy**\n\n"
                info += f"**Server:** {data.get('server', 'Unknown')}\n"
                info += f"**Version:** {data.get('version', 'Unknown')}\n"
                info += f"**Trading Available:** {'✅ Yes' if data.get('trading_available') else '❌ No'}\n"
                info += f"**Active Sessions:** {data.get('active_sessions', 0)}\n"
                info += f"**Timestamp:** {data.get('timestamp', 'Unknown')}"
                
                logger.info("✅ Backend health check passed")
                return info
            else:
                return f"❌ Backend unhealthy: {data.get('message', 'Unknown error')}"
        else:
            return f"❌ Backend error: HTTP {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Backend connection failed")
        return f"❌ Cannot connect to backend at {BACKEND_URL}"
    except Exception as e:
        logger.error(f"❌ Backend health check error: {e}")
        return f"❌ Health check error: {str(e)}"

# Create Gradio interface
def create_interface():
    """Create the Gradio interface"""

    with gr.Blocks(title="🤖 Alibaba AI Crypto Chatbot") as interface:
        gr.Markdown("# 🤖 Alibaba AI Crypto Chatbot")
        gr.Markdown("### 💰 Real-time crypto analysis and trading powered by Alibaba Cloud AI")

        with gr.Row():
            with gr.Column(scale=2):
                # Chat interface
                chatbot = gr.Chatbot(label="💬 Chat with AI", height=400)

                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Ask about crypto prices, analysis, or try trading commands like 'buy 0.01 BTC'",
                        label="Your message"
                    )
                    send_btn = gr.Button("Send 📤")

            with gr.Column(scale=1):
                # Control panel
                gr.Markdown("### 🎛️ Control Panel")

                init_btn = gr.Button("🔄 Initialize Session")
                init_status = gr.Textbox(label="Session Status", interactive=False)

                gr.Markdown("### 📊 Quick Actions")

                portfolio_btn = gr.Button("💼 View Portfolio")
                portfolio_info = gr.Textbox(label="Portfolio", lines=8, interactive=False)

                with gr.Row():
                    price_symbol = gr.Textbox(placeholder="BTC", label="Symbol")
                    price_btn = gr.Button("💲 Get Price")

                price_info = gr.Textbox(label="Price Info", lines=5, interactive=False)

                health_btn = gr.Button("🔍 Check Backend")
                health_info = gr.Textbox(label="Backend Status", lines=3, interactive=False)

        # Event handlers
        init_btn.click(
            initialize_session,
            outputs=[init_status]
        )

        send_btn.click(
            chat_with_ai,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )

        msg_input.submit(
            chat_with_ai,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )

        portfolio_btn.click(
            get_portfolio_info,
            outputs=portfolio_info
        )

        price_btn.click(
            get_crypto_price,
            inputs=price_symbol,
            outputs=price_info
        )

        health_btn.click(
            check_backend_health,
            outputs=health_info
        )

    return interface

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🌐 STARTING GRADIO FRONTEND")
    logger.info("=" * 60)
    logger.info("📡 Frontend will be available at: http://localhost:3000")
    logger.info(f"🔗 Backend API expected at: {BACKEND_URL}")
    logger.info(f"🤖 AlibabaAI: {'✅ Available' if AlibabaAI else '❌ Not Available'}")
    logger.info(f"💰 Trading: {'✅ Available' if TRADING_AVAILABLE else '❌ Not Available'}")
    logger.info("=" * 60)
    
    # Create and launch interface
    interface = create_interface()
    
    try:
        interface.launch(
            server_name="0.0.0.0",
            server_port=3000,
            share=False,
            debug=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Frontend stopped by user")
    except Exception as e:
        logger.error(f"❌ Frontend error: {e}")
    finally:
        logger.info("👋 Gradio frontend shutdown complete")
