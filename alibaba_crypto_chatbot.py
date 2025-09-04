#!/usr/bin/env python3
"""
🤖 Simple Alibaba AI Crypto Chatbot
Following the notebook pattern exactly - clean and simple
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("✅ Core libraries imported successfully!")
print(f"📅 Setup Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Alibaba AI Integration (exactly like DeepSeek in notebook)
class AlibabaAI:
    """Alibaba AI integration for comprehensive analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('ALIBABA_API_KEY')
        self.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.model = "qwen-plus"
        
        if not self.api_key:
            print("⚠️  Alibaba API key not found. Add ALIBABA_API_KEY to .env file")
            self.available = False
        else:
            print("✅ Alibaba AI initialized")
            self.available = True
    
    def get_crypto_price(self, crypto_symbol):
        """Get real-time crypto price from Binance (primary) with CoinGecko fallback"""
        # Try Binance first
        binance_result = self._get_binance_price(crypto_symbol)
        if binance_result.get('success'):
            return binance_result

        # Fallback to CoinGecko
        print(f"⚠️  Binance failed, trying CoinGecko fallback...")
        return self._get_coingecko_price(crypto_symbol)

    def _get_binance_price(self, crypto_symbol):
        """Get price from Binance API"""
        try:
            # Map symbols to Binance trading pairs
            symbol_map = {
                'BTC': 'BTCUSDT',
                'ETH': 'ETHUSDT',
                'SOL': 'SOLUSDT',
                'ADA': 'ADAUSDT',
                'MATIC': 'MATICUSDT',
                'LINK': 'LINKUSDT',
                'AVAX': 'AVAXUSDT',
                'DOT': 'DOTUSDT'
            }

            trading_pair = symbol_map.get(crypto_symbol.upper())
            if not trading_pair:
                return {'success': False, 'error': f'Symbol {crypto_symbol} not supported on Binance'}

            # Get 24hr ticker statistics
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': trading_pair}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'symbol': crypto_symbol.upper(),
                    'current_price': float(data['lastPrice']),
                    'price_change_24h': float(data['priceChangePercent']),
                    'volume_24h': float(data['volume']) * float(data['lastPrice']),  # Volume in USD
                    'high_24h': float(data['highPrice']),
                    'low_24h': float(data['lowPrice']),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Binance'
                }
            else:
                return {'success': False, 'error': f'Binance API error: {response.status_code}'}

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
    
    def chat_response(self, user_message, context_data=None):
        """Interactive chat response with context and real-time prices"""
        if not self.available:
            return {'success': False, 'error': 'Alibaba AI not available'}
        
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

# Initialize Alibaba AI
alibaba_ai = AlibabaAI()
print(f"🤖 Alibaba AI Status: {'✅ Ready' if alibaba_ai.available else '❌ Not Available'}")

def main():
    """Main chat interface following notebook pattern exactly"""
    
    # Interactive Chatbot (exactly like notebook)
    print("\n🤖 ALIBABA AI CRYPTO CHATBOT")
    print("=" * 50)
    print("Ask me anything about crypto analysis!")
    print("Examples:")
    print("- 'What's your recommendation for Bitcoin?'")
    print("- 'How is Solana doing today?'")
    print("- 'Should I buy Ethereum now?'")
    print("- 'What are the key technical levels for BTC?'")
    print("- 'Analyze the current market conditions'")
    print("\nType 'quit' to exit the chat")
    print("-" * 50)
    
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
