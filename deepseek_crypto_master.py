#!/usr/bin/env python3
"""
🤖 DeepSeek Crypto Master - Terminal Version
Complete crypto analysis platform with interactive AI chatbot

Usage:
    python deepseek_crypto_master.py
    
Features:
- Dynamic cryptocurrency analysis
- Real-time price data from Binance
- Multi-source sentiment analysis
- TradingView technical analysis
- Interactive DeepSeek AI chatbot
- Context-aware responses
"""

import sys
import os
import requests
import json
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Data processing
import pandas as pd
import numpy as np

# Web scraping
from bs4 import BeautifulSoup
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Environment
from dotenv import load_dotenv
load_dotenv()

# Import custom modules
try:
    from crypto_analysis import CryptoAnalyzer
    CRYPTO_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"❌ CryptoAnalyzer import failed: {e}")
    CRYPTO_ANALYSIS_AVAILABLE = False

try:
    from sentiment_analysis import CryptoSentimentAnalyzer
    SENTIMENT_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"❌ CryptoSentimentAnalyzer import failed: {e}")
    SENTIMENT_ANALYSIS_AVAILABLE = False

try:
    from web_scraping import WebScraper
    WEB_SCRAPING_AVAILABLE = True
except ImportError as e:
    print(f"❌ WebScraper import failed: {e}")
    WEB_SCRAPING_AVAILABLE = False

class TradingViewScraper:
    """Scrape technical analysis from TradingView"""
    
    def __init__(self):
        self.base_url = "https://www.tradingview.com/ideas/technicalanalysis/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_crypto_ideas(self, crypto_symbol="BTC", max_ideas=3):
        """Scrape crypto technical analysis ideas from TradingView"""
        print(f"📈 Scraping TradingView ideas for {crypto_symbol}...")
        
        try:
            # Try with requests first (faster)
            url = f"{self.base_url}?sort=recent&symbol={crypto_symbol}USD"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                ideas = self._extract_ideas_from_soup(soup, max_ideas)
                
                if ideas:
                    print(f"✅ Found {len(ideas)} ideas")
                    return ideas
            
            # Fallback to mock data
            print("🔄 Using mock technical analysis data")
            return self.get_mock_technical_analysis(crypto_symbol)
            
        except Exception as e:
            print(f"❌ Error scraping TradingView: {e}")
            return self.get_mock_technical_analysis(crypto_symbol)
    
    def _extract_ideas_from_soup(self, soup, max_ideas):
        """Extract ideas from BeautifulSoup object"""
        ideas = []
        
        # Look for idea containers
        idea_containers = soup.find_all(['div', 'article'], class_=lambda x: x and ('idea' in x.lower() or 'post' in x.lower()))[:max_ideas]
        
        for container in idea_containers:
            try:
                # Extract title
                title_elem = container.find(['h1', 'h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower())
                title = title_elem.get_text().strip() if title_elem else "No title"
                
                # Extract author
                author_elem = container.find(['span', 'div'], class_=lambda x: x and 'author' in x.lower())
                author = author_elem.get_text().strip() if author_elem else "Unknown"
                
                # Extract content
                content_elem = container.find(['p', 'div'], class_=lambda x: x and ('content' in x.lower() or 'description' in x.lower()))
                content = content_elem.get_text().strip() if content_elem else ""
                
                if title and title != "No title":
                    ideas.append({
                        'title': title,
                        'author': author,
                        'content': content[:200] + "..." if len(content) > 200 else content,
                        'source': 'TradingView',
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                continue
        
        return ideas
    
    def get_mock_technical_analysis(self, crypto_symbol):
        """Provide mock technical analysis if scraping fails"""
        return [
            {
                'title': f'{crypto_symbol} Technical Analysis - Current Market View',
                'author': 'TradingView Analyst',
                'content': f'{crypto_symbol} showing mixed technical signals with key levels to watch. RSI in neutral territory.',
                'source': 'TradingView (Mock)',
                'timestamp': datetime.now().isoformat()
            },
            {
                'title': f'{crypto_symbol} Price Action Analysis',
                'author': 'Technical Analyst',
                'content': f'Current {crypto_symbol} price action suggests consolidation with potential for breakout above resistance.',
                'source': 'TradingView (Mock)',
                'timestamp': datetime.now().isoformat()
            }
        ]

class DeepSeekAI:
    """DeepSeek AI integration for comprehensive analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat"
        
        if not self.api_key:
            print("⚠️  OpenRouter API key not found. Add OPENROUTER_API_KEY to .env file")
            self.available = False
        else:
            print("✅ DeepSeek AI initialized")
            self.available = True
    
    def analyze_comprehensive_data(self, crypto_name, price_data, sentiment_data, technical_analysis, web_data):
        """Comprehensive analysis using all available data"""
        if not self.available:
            return {'success': False, 'error': 'DeepSeek AI not available'}
        
        # Prepare comprehensive prompt
        prompt = f"""
As a professional cryptocurrency analyst, provide a comprehensive analysis of {crypto_name} based on the following data:

PRICE DATA:
{json.dumps(price_data, indent=2, default=str) if price_data else 'No price data available'}

SENTIMENT ANALYSIS:
{json.dumps(sentiment_data, indent=2, default=str) if sentiment_data else 'No sentiment data available'}

TECHNICAL ANALYSIS (TradingView):
{json.dumps(technical_analysis, indent=2, default=str) if technical_analysis else 'No technical analysis available'}

WEB DATA:
{json.dumps(web_data, indent=2, default=str) if web_data else 'No web data available'}

Please provide:
1. Overall market assessment
2. Key technical levels and indicators
3. Sentiment analysis interpretation
4. Trading recommendation (BUY/HOLD/SELL)
5. Risk assessment
6. Price targets and stop losses
7. Confidence level (1-10)

Format your response in a clear, professional manner suitable for trading decisions.
"""
        
        return self._make_api_call(prompt)
    
    def chat_response(self, user_message, context_data=None):
        """Interactive chat response with context"""
        if not self.available:
            return {'success': False, 'error': 'DeepSeek AI not available'}
        
        # Add context if available
        context_prompt = ""
        if context_data:
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                elif hasattr(obj, 'isoformat'):  # datetime objects
                    return obj.isoformat()
                else:
                    return obj
            
            try:
                serializable_context = convert_datetime(context_data)
                context_prompt = f"""
CONTEXT DATA:
{json.dumps(serializable_context, indent=2, default=str)}

"""
            except Exception as e:
                context_prompt = f"""
CONTEXT DATA: (Serialization error: {str(e)})
Basic context available but not serializable.

"""
        
        prompt = f"""
You are a professional cryptocurrency analyst and trading expert. Answer the user's question based on your expertise and any provided context data.

{context_prompt}
USER QUESTION: {user_message}

Provide a helpful, accurate, and professional response. If you need more specific data to give a complete answer, mention what additional information would be helpful.
"""
        
        return self._make_api_call(prompt)
    
    def _make_api_call(self, prompt):
        """Make API call to DeepSeek"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'content': content,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"API call failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"API call error: {str(e)}"
            }

def comprehensive_crypto_analysis(crypto_name, max_articles=3, max_tradingview_ideas=2):
    """
    Comprehensive crypto analysis using all available modules
    """
    print(f"🚀 Starting comprehensive analysis for {crypto_name}")
    print("=" * 60)
    
    analysis_results = {
        'crypto_name': crypto_name,
        'timestamp': datetime.now().isoformat(),
        'price_data': None,
        'sentiment_data': None,
        'technical_analysis': None,
        'web_data': None,
        'deepseek_analysis': None
    }
    
    # Initialize modules
    crypto_analyzer = CryptoAnalyzer() if CRYPTO_ANALYSIS_AVAILABLE else None
    sentiment_analyzer = CryptoSentimentAnalyzer() if SENTIMENT_ANALYSIS_AVAILABLE else None
    web_scraper = WebScraper() if WEB_SCRAPING_AVAILABLE else None
    tradingview_scraper = TradingViewScraper()
    deepseek_ai = DeepSeekAI()
    
    # 1. Crypto Analysis (Price + Technical)
    if crypto_analyzer:
        print("\n1️⃣ Getting price and technical analysis...")
        try:
            price_result = crypto_analyzer.process_query(f"What's the price of {crypto_name}?")
            if price_result.get('success'):
                analysis_results['price_data'] = price_result
                print("   ✅ Price analysis completed")
            else:
                print(f"   ❌ Price analysis failed: {price_result.get('error')}")
        except Exception as e:
            print(f"   ❌ Price analysis error: {e}")
    else:
        print("\n1️⃣ ❌ Crypto analysis module not available")
    
    # 2. Sentiment Analysis
    if sentiment_analyzer:
        print("\n2️⃣ Performing sentiment analysis...")
        try:
            sentiment_result = sentiment_analyzer.analyze_cryptocurrency(crypto_name, max_articles)
            if sentiment_result.get('success'):
                analysis_results['sentiment_data'] = sentiment_result
                print("   ✅ Sentiment analysis completed")
            else:
                print(f"   ❌ Sentiment analysis failed: {sentiment_result.get('error')}")
        except Exception as e:
            print(f"   ❌ Sentiment analysis error: {e}")
    else:
        print("\n2️⃣ ❌ Sentiment analysis module not available")
    
    # 3. TradingView Technical Analysis
    print("\n3️⃣ Scraping TradingView technical analysis...")
    try:
        # Extract ticker symbol from crypto name
        ticker_map = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL',
            'cardano': 'ADA', 'polygon': 'MATIC', 'chainlink': 'LINK',
            'avalanche': 'AVAX', 'polkadot': 'DOT'
        }
        ticker = ticker_map.get(crypto_name.lower(), crypto_name.upper()[:3])
        
        technical_ideas = tradingview_scraper.scrape_crypto_ideas(ticker, max_tradingview_ideas)
        analysis_results['technical_analysis'] = technical_ideas
        print(f"   ✅ Found {len(technical_ideas)} technical analysis ideas")
        
    except Exception as e:
        print(f"   ❌ TradingView scraping error: {e}")
    
    # 4. Web Scraping
    if web_scraper:
        print("\n4️⃣ Performing additional web scraping...")
        try:
            # Get crypto news
            news_data = web_scraper.scrape_crypto_news(limit=2)
            
            # Get price data from multiple sources
            price_data = web_scraper.scrape_crypto_prices([ticker])
            
            analysis_results['web_data'] = {
                'news': news_data,
                'prices': price_data
            }
            print(f"   ✅ Scraped {len(news_data)} news items and {len(price_data)} price entries")
            
        except Exception as e:
            print(f"   ❌ Web scraping error: {e}")
    else:
        print("\n4️⃣ ❌ Web scraping module not available")
    
    # 5. DeepSeek Comprehensive Analysis
    if deepseek_ai.available:
        print("\n5️⃣ Generating DeepSeek AI comprehensive analysis...")
        try:
            deepseek_result = deepseek_ai.analyze_comprehensive_data(
                crypto_name,
                analysis_results['price_data'],
                analysis_results['sentiment_data'],
                analysis_results['technical_analysis'],
                analysis_results['web_data']
            )
            
            if deepseek_result.get('success'):
                analysis_results['deepseek_analysis'] = deepseek_result
                print("   ✅ DeepSeek analysis completed")
            else:
                print(f"   ❌ DeepSeek analysis failed: {deepseek_result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ DeepSeek analysis error: {e}")
    else:
        print("\n5️⃣ ❌ DeepSeek AI not available")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive analysis completed!")
    
    return analysis_results

def display_analysis_results(results):
    """
    Display comprehensive analysis results in a formatted way
    """
    print(f"\n📊 COMPREHENSIVE ANALYSIS RESULTS FOR {results['crypto_name'].upper()}")
    print("=" * 60)
    print(f"📅 Analysis Time: {results['timestamp'][:19]}")
    
    # Price Data
    if results['price_data']:
        price_data = results['price_data'].get('price_data', {})
        if price_data:
            print(f"\n💰 PRICE DATA:")
            current_price = price_data.get('current_price', 'N/A')
            change_24h = price_data.get('price_change_24h', 'N/A')
            
            if isinstance(current_price, (int, float)):
                print(f"   Current Price: ${current_price:,.2f}")
            else:
                print(f"   Current Price: {current_price}")
                
            if isinstance(change_24h, (int, float)):
                print(f"   24h Change: {change_24h:+.2f}%")
            else:
                print(f"   24h Change: {change_24h}")
    
    # Sentiment Data
    if results['sentiment_data']:
        sentiment = results['sentiment_data']
        print(f"\n🔍 SENTIMENT ANALYSIS:")
        print(f"   Articles Analyzed: {sentiment.get('articles_analyzed', 'N/A')}")
        
        if 'vader' in sentiment:
            vader = sentiment['vader']
            print(f"   VADER Sentiment: {vader['sentiment']} ({vader['average_score']:.3f})")
        
        if 'textblob' in sentiment:
            textblob = sentiment['textblob']
            print(f"   TextBlob Sentiment: {textblob['sentiment']} ({textblob['average_score']:.3f})")
    
    # Technical Analysis
    if results['technical_analysis']:
        print(f"\n📈 TRADINGVIEW TECHNICAL ANALYSIS:")
        for i, idea in enumerate(results['technical_analysis'][:2], 1):
            print(f"   {i}. {idea['title'][:50]}...")
            print(f"      Author: {idea['author']}")
    
    # DeepSeek Analysis
    if results['deepseek_analysis'] and results['deepseek_analysis'].get('success'):
        print(f"\n🤖 DEEPSEEK AI ANALYSIS:")
        print("─" * 50)
        print(results['deepseek_analysis']['content'])
        print("─" * 50)
    
    print("\n" + "=" * 60)

def main():
    """Main function for terminal interface"""
    print("🤖 DEEPSEEK CRYPTO MASTER - TERMINAL VERSION")
    print("=" * 60)
    print("Complete crypto analysis platform with AI chatbot")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check module availability
    print(f"\n🔧 Module Status:")
    print(f"📊 Crypto Analysis: {'✅' if CRYPTO_ANALYSIS_AVAILABLE else '❌'}")
    print(f"🔍 Sentiment Analysis: {'✅' if SENTIMENT_ANALYSIS_AVAILABLE else '❌'}")
    print(f"🌐 Web Scraping: {'✅' if WEB_SCRAPING_AVAILABLE else '❌'}")
    print(f"🤖 DeepSeek AI: {'✅' if os.getenv('OPENROUTER_API_KEY') else '❌'}")
    
    # Initialize global context
    CURRENT_ANALYSIS_CONTEXT = None
    
    # Interactive chatbot
    print(f"\n🤖 DEEPSEEK CRYPTO CHATBOT")
    print("=" * 40)
    print("Ask me anything about crypto analysis!")
    print("Examples:")
    print("- 'How is Bitcoin doing today?'")
    print("- 'What's your Solana recommendation?'")
    print("- 'Should I buy Ethereum now?'")
    print("- 'Analyze Cardano for me'")
    print("\nType 'quit' to exit")
    print("-" * 40)
    
    # Chat loop
    chat_history = []
    deepseek_ai = DeepSeekAI()
    
    while True:
        try:
            # Get user input
            user_message = input("\n💬 You: ").strip()
            
            if user_message.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for using DeepSeek Crypto Master!")
                break
            
            if not user_message:
                print("⚠️  Please enter a message")
                continue
            
            # Add to chat history
            chat_history.append({
                "role": "user", 
                "message": user_message, 
                "timestamp": datetime.now().isoformat()
            })
            
            print("\n🤖 DeepSeek: Thinking...")
            
            # Check if user is asking about a different cryptocurrency
            def extract_crypto_from_message(message):
                """Extract cryptocurrency name from user message"""
                message_lower = message.lower()
                crypto_keywords = {
                    'bitcoin': 'Bitcoin', 'btc': 'Bitcoin',
                    'ethereum': 'Ethereum', 'eth': 'Ethereum',
                    'solana': 'Solana', 'sol': 'Solana',
                    'cardano': 'Cardano', 'ada': 'Cardano',
                    'polygon': 'Polygon', 'matic': 'Polygon',
                    'chainlink': 'Chainlink', 'link': 'Chainlink',
                    'avalanche': 'Avalanche', 'avax': 'Avalanche',
                    'polkadot': 'Polkadot', 'dot': 'Polkadot'
                }
                
                for keyword, crypto_name in crypto_keywords.items():
                    if keyword in message_lower:
                        return crypto_name
                return None
            
            # Check if we need to analyze a different crypto
            requested_crypto = extract_crypto_from_message(user_message)
            current_crypto = CURRENT_ANALYSIS_CONTEXT.get('crypto_name', '') if CURRENT_ANALYSIS_CONTEXT else ''
            
            # If user asks about a different crypto, run new analysis
            if requested_crypto and requested_crypto.lower() != current_crypto.lower():
                print(f"🔄 Analyzing {requested_crypto} (different from current analysis)...")
                try:
                    # Run comprehensive analysis for the requested crypto
                    new_analysis = comprehensive_crypto_analysis(requested_crypto, max_articles=3, max_tradingview_ideas=2)
                    # Update global context
                    CURRENT_ANALYSIS_CONTEXT = new_analysis
                    print(f"✅ {requested_crypto} analysis completed!")
                except Exception as e:
                    print(f"❌ Error analyzing {requested_crypto}: {e}")
            
            # Get AI response with context
            if deepseek_ai.available:
                # Prepare context data
                context_data = {
                    'current_analysis': CURRENT_ANALYSIS_CONTEXT,
                    'chat_history': chat_history[-3:] if len(chat_history) > 3 else chat_history
                }
                
                response = deepseek_ai.chat_response(user_message, context_data)
                
                if response.get('success'):
                    ai_message = response['content']
                    print(f"\n🤖 DeepSeek: {ai_message}")
                    
                    # Add AI response to history
                    chat_history.append({
                        "role": "assistant", 
                        "message": ai_message, 
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    print(f"\n❌ Error: {response.get('error')}")
            else:
                print("\n❌ DeepSeek AI is not available. Please check your OPENROUTER_API_KEY in .env file")
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Thanks for using DeepSeek Crypto Master!")
            break
        except Exception as e:
            print(f"\n❌ Chat error: {e}")
            continue
    
    print(f"\n📊 Chat session ended.")
    print(f"💬 Total messages exchanged: {len(chat_history)}")

if __name__ == "__main__":
    main()
