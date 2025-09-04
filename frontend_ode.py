"""Frontend example for Alibaba Crypto Chatbot API"""
#!/usr/bin/env python3
"""
🤖 Simple Alibaba AI Crypto Chatbot
Following the notebook pattern exactly - clean and simple
"""

import os
import requests
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Optional, List

# Import trading engine
try:
    from crypto_trading_engine import TradingEngine, TradeCommandParser
    TRADING_AVAILABLE = True
    print("✅ Trading engine imported successfully!")
except ImportError as e:
    print(f"⚠️  Trading engine not available: {e}")
    TRADING_AVAILABLE = False

# Load environment
load_dotenv()

print("✅ Core libraries imported successfully!")
print(f"📅 Setup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🔄 Trading Engine: {'✅ Available' if TRADING_AVAILABLE else '❌ Not Available'}")

# Alibaba AI Integration (exactly like DeepSeek in notebook)
class AlibabaAI:
    """Alibaba AI integration for comprehensive analysis and trading"""

    def __init__(self, user_id: str = "default_user"):
        self.api_key = os.getenv('ALIBABA_API_KEY')
        self.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model = "qwen-plus"
        self.user_id = user_id

        # Initialize trading engine
        if TRADING_AVAILABLE:
            self.trading_engine = TradingEngine()
            self.trade_parser = TradeCommandParser()
            print("✅ Trading engine initialized")
        else:
            self.trading_engine = None
            self.trade_parser = None

        if not self.api_key:
            print("⚠️  Alibaba API key not found. Add ALIBABA_API_KEY to .env file")
            self.available = False
        else:
            print("✅ Alibaba AI initialized")
            self.available = True
    
    def get_crypto_price(self, crypto_symbol):
        """Enhanced crypto price fetching with smart symbol recognition"""
        # Normalize and enhance symbol recognition
        normalized_symbol = self._normalize_crypto_symbol(crypto_symbol)
        if not normalized_symbol:
            return {
                'success': False,
                'error': f'Unsupported cryptocurrency: {crypto_symbol}. Supported: BTC, ETH, SOL, ADA, MATIC, LINK, AVAX, DOT'
            }

        # Try Binance first
        binance_result = self._get_binance_price(normalized_symbol)
        if binance_result.get('success'):
            return binance_result

        # Fallback to CoinGecko
        print(f"⚠️  Binance failed for {normalized_symbol}, trying CoinGecko fallback...")
        return self._get_coingecko_price(normalized_symbol)

    def _normalize_crypto_symbol(self, symbol: str) -> Optional[str]:
        """Enhanced symbol normalization with natural language support"""
        if not symbol:
            return None

        symbol = symbol.lower().strip()

        # Enhanced symbol mapping with natural language
        symbol_map = {
            # Standard symbols
            'btc': 'BTC', 'bitcoin': 'BTC', 'bitcoins': 'BTC',
            'eth': 'ETH', 'ethereum': 'ETH', 'ether': 'ETH',
            'sol': 'SOL', 'solana': 'SOL',
            'ada': 'ADA', 'cardano': 'ADA',
            'matic': 'MATIC', 'polygon': 'MATIC', 'poly': 'MATIC',
            'link': 'LINK', 'chainlink': 'LINK',
            'avax': 'AVAX', 'avalanche': 'AVAX',
            'dot': 'DOT', 'polkadot': 'DOT',

            # Common variations
            'btc-usd': 'BTC', 'btcusd': 'BTC', 'btc/usd': 'BTC',
            'eth-usd': 'ETH', 'ethusd': 'ETH', 'eth/usd': 'ETH',
            'sol-usd': 'SOL', 'solusd': 'SOL', 'sol/usd': 'SOL',

            # Slang and common names
            'bitcoin cash': 'BTC',  # Note: This is simplified
            'digital gold': 'BTC',
            'world computer': 'ETH',
            'ethereum killer': 'SOL',
        }

        return symbol_map.get(symbol, symbol.upper() if len(symbol) <= 5 else None)

    def _get_binance_price(self, crypto_symbol):
        """Enhanced Binance API with better error handling and more data"""
        try:
            # Enhanced symbol mapping with more pairs
            symbol_map = {
                'BTC': 'BTCUSDT',
                'ETH': 'ETHUSDT',
                'SOL': 'SOLUSDT',
                'ADA': 'ADAUSDT',
                'MATIC': 'MATICUSDT',
                'LINK': 'LINKUSDT',
                'AVAX': 'AVAXUSDT',
                'DOT': 'DOTUSDT',
                # Additional popular pairs
                'BNB': 'BNBUSDT',
                'XRP': 'XRPUSDT',
                'DOGE': 'DOGEUSDT',
                'SHIB': 'SHIBUSDT',
                'UNI': 'UNIUSDT',
                'ATOM': 'ATOMUSDT'
            }

            trading_pair = symbol_map.get(crypto_symbol.upper())
            if not trading_pair:
                return {'success': False, 'error': f'Symbol {crypto_symbol} not supported on Binance'}

            # Get 24hr ticker statistics with retry logic
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': trading_pair}

            for attempt in range(3):  # Retry up to 3 times
                try:
                    response = requests.get(url, params=params, timeout=10)

                    if response.status_code == 200:
                        data = response.json()

                        # Enhanced data with additional metrics
                        result = {
                            'success': True,
                            'symbol': crypto_symbol.upper(),
                            'current_price': float(data['lastPrice']),
                            'price_change_24h': float(data['priceChangePercent']),
                            'price_change_abs': float(data['priceChange']),
                            'volume_24h': float(data['volume']) * float(data['lastPrice']),  # Volume in USD
                            'volume_24h_base': float(data['volume']),  # Volume in base currency
                            'high_24h': float(data['highPrice']),
                            'low_24h': float(data['lowPrice']),
                            'open_price': float(data['openPrice']),
                            'prev_close': float(data['prevClosePrice']),
                            'bid_price': float(data['bidPrice']) if 'bidPrice' in data else None,
                            'ask_price': float(data['askPrice']) if 'askPrice' in data else None,
                            'trade_count': int(data['count']),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'Binance',
                            'trading_pair': trading_pair
                        }

                        # Add price trend analysis
                        if result['price_change_24h'] > 5:
                            result['trend'] = 'Strong Bullish'
                        elif result['price_change_24h'] > 2:
                            result['trend'] = 'Bullish'
                        elif result['price_change_24h'] > -2:
                            result['trend'] = 'Neutral'
                        elif result['price_change_24h'] > -5:
                            result['trend'] = 'Bearish'
                        else:
                            result['trend'] = 'Strong Bearish'

                        return result

                    elif response.status_code == 429:  # Rate limit
                        if attempt < 2:
                            time.sleep(1)  # Wait before retry
                            continue
                        return {'success': False, 'error': 'Binance rate limit exceeded'}
                    else:
                        return {'success': False, 'error': f'Binance API error: {response.status_code}'}

                except requests.exceptions.Timeout:
                    if attempt < 2:
                        continue
                    return {'success': False, 'error': 'Binance API timeout'}

        except Exception as e:
            return {'success': False, 'error': f'Binance fetch error: {str(e)}'}

    def _get_coingecko_price(self, crypto_symbol):
        """Get price from CoinGecko API (fallback)"""
        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'SOL': 'solana',
                'ADA': 'cardano',
                'MATIC': 'polygon',
                'LINK': 'chainlink',
                'AVAX': 'avalanche-2',
                'DOT': 'polkadot'
            }

            coin_id = symbol_map.get(crypto_symbol.upper(), crypto_symbol.lower())

            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    price_info = data[coin_id]
                    return {
                        'success': True,
                        'symbol': crypto_symbol.upper(),
                        'current_price': price_info.get('usd', 0),
                        'price_change_24h': price_info.get('usd_24h_change', 0),
                        'market_cap': price_info.get('usd_market_cap', 0),
                        'volume_24h': price_info.get('usd_24h_vol', 0),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'CoinGecko'
                    }

            return {'success': False, 'error': 'CoinGecko: Price data not found'}

        except Exception as e:
            return {'success': False, 'error': f'CoinGecko fetch error: {str(e)}'}

    def execute_trade(self, trade_type: str, symbol: str, amount: float) -> Dict:
        """Execute a trade through the trading engine"""
        if not TRADING_AVAILABLE or not self.trading_engine:
            return {
                'success': False,
                'error': 'Trading engine not available'
            }

        # Get current price for the symbol
        price_data = self.get_crypto_price(symbol)
        if not price_data.get('success'):
            return {
                'success': False,
                'error': f'Could not get price for {symbol}: {price_data.get("error")}'
            }

        current_price = price_data['current_price']

        # Handle "sell all" case
        if trade_type.upper() == 'SELL' and amount == 'ALL':
            portfolio = self.trading_engine.get_or_create_portfolio(self.user_id)
            amount = portfolio.get_holding(symbol)
            if amount == 0:
                return {
                    'success': False,
                    'error': f'No {symbol} holdings to sell'
                }

        # Execute the trade
        result = self.trading_engine.execute_trade(
            self.user_id, trade_type, symbol, amount, current_price
        )

        return result

    def get_portfolio(self) -> Dict:
        """Get current portfolio status"""
        if not TRADING_AVAILABLE or not self.trading_engine:
            return {
                'success': False,
                'error': 'Trading engine not available'
            }

        portfolio = self.trading_engine.get_or_create_portfolio(self.user_id)

        # Get current prices for all holdings
        price_data = {}
        for symbol in portfolio.holdings.keys():
            price_result = self.get_crypto_price(symbol)
            if price_result.get('success'):
                price_data[symbol] = price_result['current_price']

        portfolio_value = portfolio.get_portfolio_value(price_data)

        return {
            'success': True,
            'portfolio': portfolio.to_dict(),
            'portfolio_value': portfolio_value,
            'timestamp': datetime.now().isoformat()
        }

    def chat_response(self, user_message, context_data=None):
        """Interactive chat response with context, real-time prices, and trading"""
        if not self.available:
            return {'success': False, 'error': 'Alibaba AI not available'}

        # Check for trading commands first
        if TRADING_AVAILABLE and self.trade_parser:
            trade_command = self.trade_parser.parse_trade_command(user_message)
            if trade_command:
                return self._handle_trade_command(trade_command, user_message)

        # Check for portfolio commands
        if any(word in user_message.lower() for word in ['portfolio', 'balance', 'holdings', 'my coins']):
            return self._handle_portfolio_request(user_message)

        # Check if user is asking about a specific crypto
        crypto_symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'MATIC', 'LINK', 'AVAX', 'DOT', 'BITCOIN', 'ETHEREUM', 'SOLANA']
        mentioned_crypto = None

        for symbol in crypto_symbols:
            if symbol.lower() in user_message.lower():
                mentioned_crypto = symbol[:3] if len(symbol) > 3 else symbol
                break
        
        # Get real-time price if crypto mentioned
        price_data = None
        if mentioned_crypto:
            price_result = self.get_crypto_price(mentioned_crypto)
            if price_result.get('success'):
                price_data = price_result
        
        # Build context-aware prompt
        prompt_parts = []
        
        # Add system context
        prompt_parts.append("You are a professional cryptocurrency analyst and trading advisor with access to real-time market data.")
        
        # Add real-time price data if available
        if price_data:
            data_source = price_data.get('source', 'Unknown')
            prompt_parts.append(f"\nREAL-TIME PRICE DATA for {price_data['symbol']} (Source: {data_source}):")
            prompt_parts.append(f"Current Price: ${price_data['current_price']:,.2f}")
            prompt_parts.append(f"24h Change: {price_data['price_change_24h']:+.2f}%")

            # Add market cap if available (CoinGecko)
            if 'market_cap' in price_data and price_data['market_cap']:
                prompt_parts.append(f"Market Cap: ${price_data['market_cap']:,.0f}")

            # Add volume
            prompt_parts.append(f"24h Volume: ${price_data['volume_24h']:,.0f}")

            # Add high/low if available (Binance)
            if 'high_24h' in price_data:
                prompt_parts.append(f"24h High: ${price_data['high_24h']:,.2f}")
                prompt_parts.append(f"24h Low: ${price_data['low_24h']:,.2f}")

            prompt_parts.append(f"Data Time: {price_data['timestamp']}")
        
        # Add context data if available
        if context_data:
            if 'chat_history' in context_data:
                history = context_data['chat_history']
                if history:
                    prompt_parts.append(f"\nRecent conversation context: {json.dumps(history[-2:], indent=2)}")
        
        # Add the actual user message
        prompt_parts.append(f"\nUser question: {user_message}")
        
        # Add instructions
        if price_data:
            prompt_parts.append(f"\nProvide analysis using the real-time price data above for {price_data['symbol']}. Include current market conditions, price trends, and actionable insights.")
        else:
            prompt_parts.append("\nProvide helpful cryptocurrency analysis. If specific price data is needed, mention that real-time data would enhance the analysis.")
        
        prompt = "\n".join(prompt_parts)
        return self._make_api_call(prompt)

    def _handle_trade_command(self, trade_command: Dict, original_message: str) -> Dict:
        """Handle trading commands"""
        action = trade_command['action']
        symbol = trade_command['symbol']
        amount = trade_command['amount']

        # Execute the trade
        trade_result = self.execute_trade(action, symbol, amount)

        if trade_result['success']:
            transaction = trade_result['transaction']
            portfolio = trade_result['portfolio_summary']

            response_text = f"✅ **Trade Executed Successfully!**\n\n"
            response_text += f"**{action}** {transaction['amount']} {symbol} at ${transaction['price']:,.2f}\n"
            response_text += f"**Total:** ${transaction['total']:,.2f}\n"
            response_text += f"**New Balance:** ${transaction['balance_after']:,.2f}\n"

            if action == 'BUY':
                response_text += f"**New {symbol} Holdings:** {trade_result['new_holding']}\n"
            else:
                response_text += f"**Remaining {symbol}:** {trade_result['new_holding']}\n"

            response_text += f"\n💼 **Portfolio Summary:**\n"
            response_text += f"Cash: ${portfolio['cash_balance']:,.2f}\n"
            response_text += f"Total Transactions: {portfolio['transaction_count']}"

            return {
                'success': True,
                'content': response_text,
                'trade_executed': True,
                'trade_details': trade_result,
                'timestamp': datetime.now().isoformat(),
                'model': self.model,
                'provider': 'Alibaba Cloud + Trading Engine'
            }
        else:
            error_text = f"❌ **Trade Failed**\n\n"
            error_text += f"Command: {original_message}\n"
            error_text += f"Error: {trade_result['error']}\n\n"
            error_text += "Please check your balance and try again."

            return {
                'success': True,
                'content': error_text,
                'trade_executed': False,
                'error_details': trade_result,
                'timestamp': datetime.now().isoformat(),
                'model': self.model,
                'provider': 'Alibaba Cloud + Trading Engine'
            }

    def _handle_portfolio_request(self, message: str) -> Dict:
        """Handle portfolio status requests"""
        portfolio_result = self.get_portfolio()

        if portfolio_result['success']:
            portfolio = portfolio_result['portfolio']
            portfolio_value = portfolio_result['portfolio_value']

            response_text = f"💼 **Your Portfolio**\n\n"
            response_text += f"**Cash Balance:** ${portfolio['cash_balance']:,.2f}\n"
            response_text += f"**Crypto Value:** ${portfolio_value['crypto_value']:,.2f}\n"
            response_text += f"**Total Value:** ${portfolio_value['total_value']:,.2f}\n\n"

            if portfolio['holdings']:
                response_text += "**Holdings:**\n"
                for symbol, details in portfolio_value['holdings_detail'].items():
                    response_text += f"• {symbol}: {details['amount']:.6f} (${details['value']:,.2f})\n"
            else:
                response_text += "**Holdings:** None (100% cash)\n"

            response_text += f"\n**Total Transactions:** {portfolio['transaction_count']}"

            return {
                'success': True,
                'content': response_text,
                'portfolio_data': portfolio_result,
                'timestamp': datetime.now().isoformat(),
                'model': self.model,
                'provider': 'Alibaba Cloud + Trading Engine'
            }
        else:
            return {
                'success': True,
                'content': f"❌ Could not retrieve portfolio: {portfolio_result['error']}",
                'timestamp': datetime.now().isoformat(),
                'model': self.model,
                'provider': 'Alibaba Cloud + Trading Engine'
            }

    def _make_api_call(self, prompt):
        """Make API call to Alibaba Cloud"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency analyst and trading advisor."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return {
                        'success': True,
                        'content': content,
                        'timestamp': datetime.now().isoformat(),
                        'model': self.model,
                        'provider': 'Alibaba Cloud'
                    }
            
            return {
                'success': False,
                'error': f"API call failed: {response.status_code} - {response.text}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"API call error: {str(e)}"
            }

# Initialize Alibaba AI with unique user ID
user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
alibaba_ai = AlibabaAI(user_id=user_id)
print(f"🤖 Alibaba AI Status: {'✅ Ready' if alibaba_ai.available else '❌ Not Available'}")
print(f"👤 User ID: {user_id}")

def main():
    """Main chat interface following notebook pattern exactly"""
    
    # Interactive Chatbot with Trading
    print("\n🤖 ALIBABA AI CRYPTO CHATBOT + TRADING")
    print("=" * 60)
    print("Ask me anything about crypto analysis and execute trades!")
    print("\n📊 Analysis Examples:")
    print("- 'What's your recommendation for Bitcoin?'")
    print("- 'How is Solana doing today?'")
    print("- 'Should I buy Ethereum now?'")
    print("- 'What are the key technical levels for BTC?'")

    if TRADING_AVAILABLE:
        print("\n💰 Trading Examples:")
        print("- 'buy 0.1 BTC'")
        print("- 'sell 0.5 ETH'")
        print("- 'purchase 2 SOL'")
        print("- 'sell all ADA'")
        print("- 'show my portfolio'")
        print("- 'what's my balance'")
    else:
        print("\n⚠️  Trading not available (crypto_trading_engine.py not found)")

    print("\nType 'quit' to exit the chat")
    print("-" * 60)
    
    # Chat loop (exactly like notebook)
    chat_history = []
    
    while True:
        try:
            # Get user input
            user_message = input("\n💬 You: ").strip()
            
            if user_message.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for using Alibaba AI Crypto Chatbot!")
                break
            
            if not user_message:
                print("⚠️  Please enter a message")
                continue
            
            # Add to chat history
            chat_history.append({"role": "user", "message": user_message, "timestamp": datetime.now().isoformat()})
            
            print("\n🤖 Alibaba AI: Thinking...")
            
            # Get AI response with context
            if alibaba_ai.available:
                # Prepare context data
                context_data = {
                    'chat_history': chat_history[-3:] if len(chat_history) > 3 else chat_history  # Last 3 messages for context
                }
                
                response = alibaba_ai.chat_response(user_message, context_data)
                
                if response.get('success'):
                    ai_message = response['content']
                    print(f"\n🤖 Alibaba AI: {ai_message}")
                    
                    # Add AI response to history
                    chat_history.append({"role": "assistant", "message": ai_message, "timestamp": datetime.now().isoformat()})
                else:
                    print(f"\n❌ Error: {response.get('error')}")
            else:
                print("\n❌ Alibaba AI is not available. Please check your ALIBABA_API_KEY in .env file")
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Thanks for using Alibaba AI Crypto Chatbot!")
            break
        except Exception as e:
            print(f"\n❌ Chat error: {e}")
            continue
    
    print("\n📊 Chat session ended.")
    print(f"💬 Total messages exchanged: {len(chat_history)}")

if __name__ == "__main__":
    main()