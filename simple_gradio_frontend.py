#!/usr/bin/env python3
"""
🌐 Simple Gradio Frontend for Alibaba AI Crypto Chatbot
Compatible with Python 3.9.5, runs on port 3000
"""

import os
import sys
import logging
import gradio as gr
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - FRONTEND:3000 - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info("🌐 Starting Simple Gradio Frontend...")

# Import the AlibabaAI class from frontend_ode
try:
    from frontend_ode import AlibabaAI, TRADING_AVAILABLE
    logger.info("✅ AlibabaAI imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import AlibabaAI: {e}")
    AlibabaAI = None
    TRADING_AVAILABLE = False

# Global session
current_session = None
chat_history = []

def initialize_session():
    """Initialize a new AlibabaAI session"""
    global current_session, chat_history
    
    try:
        logger.info("🔄 Initializing session")
        
        if AlibabaAI is None:
            return "❌ AlibabaAI not available"
        
        user_id = f"gradio_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        current_session = AlibabaAI(user_id=user_id)
        chat_history = []
        
        if current_session.available:
            status = f"✅ Session ready!\n👤 User: {user_id}\n💰 Trading: {'✅' if TRADING_AVAILABLE else '❌'}"
            logger.info(f"✅ Session created: {user_id}")
            return status
        else:
            return "❌ Session failed - check API key"
            
    except Exception as e:
        logger.error(f"❌ Session error: {e}")
        return f"❌ Error: {str(e)}"

def chat_with_ai(message, history):
    """Handle chat with AI"""
    global current_session, chat_history
    
    if not message.strip():
        return history, ""
    
    if current_session is None:
        history.append([message, "❌ Please initialize session first"])
        return history, ""
    
    try:
        logger.info(f"📥 Message: {message}")
        
        # Add to chat history
        chat_history.append({"role": "user", "message": message, "timestamp": datetime.now().isoformat()})
        
        # Get AI response
        context_data = {'chat_history': chat_history[-3:]}
        response = current_session.chat_response(message, context_data)
        
        if response.get('success'):
            ai_message = response['content']
            chat_history.append({"role": "assistant", "message": ai_message, "timestamp": datetime.now().isoformat()})
            
            if response.get('trade_executed'):
                ai_message += "\n\n✅ **Trade executed!**"
                logger.info("💰 Trade executed")
            
            history.append([message, ai_message])
            return history, ""
        else:
            error_msg = f"❌ Error: {response.get('error', 'Unknown')}"
            history.append([message, error_msg])
            return history, ""
            
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        history.append([message, f"❌ Error: {str(e)}"])
        return history, ""

def get_portfolio():
    """Get portfolio info"""
    global current_session
    
    if current_session is None:
        return "❌ No session"
    
    if not TRADING_AVAILABLE:
        return "❌ Trading not available"
    
    try:
        result = current_session.get_portfolio()
        if result.get('success'):
            portfolio = result['portfolio']
            portfolio_value = result['portfolio_value']
            
            info = f"💼 **Portfolio**\n\n"
            info += f"Cash: ${portfolio['cash_balance']:,.2f}\n"
            info += f"Crypto: ${portfolio_value['crypto_value']:,.2f}\n"
            info += f"Total: ${portfolio_value['total_value']:,.2f}\n\n"
            
            if portfolio['holdings']:
                info += "**Holdings:**\n"
                for symbol, details in portfolio_value['holdings_detail'].items():
                    info += f"• {symbol}: {details['amount']:.6f} (${details['value']:,.2f})\n"
            else:
                info += "No crypto holdings\n"
            
            info += f"\nTransactions: {portfolio['transaction_count']}"
            return info
        else:
            return f"❌ Portfolio error: {result.get('error')}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_price(symbol):
    """Get crypto price"""
    global current_session
    
    if not symbol.strip():
        return "Enter a symbol (BTC, ETH, SOL, etc.)"
    
    if current_session is None:
        return "❌ No session"
    
    try:
        result = current_session.get_crypto_price(symbol.strip())
        if result.get('success'):
            info = f"💰 **{result['symbol']}**\n\n"
            info += f"Price: ${result['current_price']:,.2f}\n"
            info += f"24h Change: {result['price_change_24h']:+.2f}%\n"
            
            if 'high_24h' in result:
                info += f"24h High: ${result['high_24h']:,.2f}\n"
                info += f"24h Low: ${result['low_24h']:,.2f}\n"
            
            info += f"Source: {result.get('source', 'Unknown')}"
            return info
        else:
            return f"❌ Price error: {result.get('error')}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create interface
def create_app():
    """Create the Gradio app"""
    
    with gr.Blocks(title="🤖 Alibaba AI Crypto Chatbot") as app:
        gr.Markdown("# 🤖 Alibaba AI Crypto Chatbot")
        gr.Markdown("### 💰 Real-time crypto analysis and trading")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Main chat
                chatbot = gr.Chatbot(label="💬 Chat", height=400)
                msg_input = gr.Textbox(
                    placeholder="Ask about crypto or try 'buy 0.01 BTC'",
                    label="Message"
                )
                send_btn = gr.Button("Send 📤")
                
            with gr.Column(scale=1):
                # Controls
                gr.Markdown("### 🎛️ Controls")
                init_btn = gr.Button("🔄 Initialize Session")
                session_status = gr.Textbox(label="Session", interactive=False)
                
                gr.Markdown("### 📊 Quick Actions")
                portfolio_btn = gr.Button("💼 Portfolio")
                portfolio_display = gr.Textbox(label="Portfolio", lines=8, interactive=False)
                
                price_input = gr.Textbox(placeholder="BTC", label="Symbol")
                price_btn = gr.Button("💲 Price")
                price_display = gr.Textbox(label="Price", lines=5, interactive=False)
        
        # Event handlers
        init_btn.click(initialize_session, outputs=session_status)
        
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
        
        portfolio_btn.click(get_portfolio, outputs=portfolio_display)
        price_btn.click(get_price, inputs=price_input, outputs=price_display)
        
        # Examples
        gr.Examples(
            examples=[
                "What's Bitcoin doing today?",
                "Should I buy Ethereum?",
                "buy 0.01 BTC",
                "show my portfolio"
            ],
            inputs=msg_input
        )
    
    return app

if __name__ == "__main__":
    logger.info("🚀 Starting Simple Gradio Frontend on port 3000")
    logger.info(f"🤖 AlibabaAI: {'✅' if AlibabaAI else '❌'}")
    logger.info(f"💰 Trading: {'✅' if TRADING_AVAILABLE else '❌'}")
    
    app = create_app()
    
    try:
        app.launch(
            server_name="0.0.0.0",
            server_port=3000,
            share=False
        )
    except Exception as e:
        logger.error(f"❌ Launch error: {e}")
    finally:
        logger.info("👋 Frontend shutdown")
