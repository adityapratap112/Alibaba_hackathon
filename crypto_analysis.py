"""
🚀 Crypto Analysis Module
Extracted from crypto_trading_platform/data/crypto_analysis.ipynb

This module provides functions for:
1. Ticker extraction using AI
2. Current price fetching from Binance
3. AI-powered market analysis
4. Data visualization
"""

import sys
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from openrouter_config import openrouter_config
    from binance_api import BinanceAPI
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    MODULES_AVAILABLE = False

class CryptoAnalyzer:
    """Main crypto analysis class"""

    def __init__(self):
        """Initialize the analyzer"""
        if not MODULES_AVAILABLE:
            raise ImportError("Required modules not available")

        self.binance_client = BinanceAPI()
        self.openrouter = openrouter_config

    def test_connections(self):
        """Test API connections"""
        results = {
            'openrouter': False,
            'binance': False
        }

        print("🤖 Testing OpenRouter (DeepSeek) Connection:")
        try:
            if self.openrouter.test_connection():
                print("✅ OpenRouter connection successful!")
                results['openrouter'] = True
            else:
                print("❌ OpenRouter connection failed! Please check your OPENROUTER_API_KEY in .env")
        except Exception as e:
            print(f"❌ OpenRouter error: {e}")

        print("\n📊 Testing Binance API Connection:")
        try:
            if self.binance_client.test_connection():
                print("✅ Binance API connection successful!")
                results['binance'] = True
            else:
                print("❌ Binance API connection failed!")
        except Exception as e:
            print(f"❌ Binance API error: {e}")

        return results

    def extract_ticker(self, user_query):
        """Extract cryptocurrency ticker from user query using AI"""
        print("1️⃣ Extracting cryptocurrency ticker...")
        try:
            ticker_result = self.openrouter.extract_crypto_ticker(user_query)

            if ticker_result.get('success'):
                ticker = ticker_result['ticker']
                print(f"✅ Extracted ticker: {ticker}")
                return {'success': True, 'ticker': ticker}
            else:
                error_msg = ticker_result.get('error', 'Unknown error')
                print(f"❌ Failed to extract ticker: {error_msg}")
                return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error extracting ticker: {e}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

    def get_current_price(self, ticker):
        """Fetch current price data from Binance"""
        print(f"2️⃣ Fetching current price for {ticker}...")
        try:
            price_data = self.binance_client.get_current_price(ticker)

            if price_data.get('success'):
                print(f"✅ Current price data fetched successfully!")
                print(f"   💰 Price: ${price_data['current_price']:,.2f}")
                print(f"   📈 24h Change: {price_data['price_change_24h']:+.2f}%")
                print(f"   📊 24h High/Low: ${price_data['high_24h']:,.2f} / ${price_data['low_24h']:,.2f}")
                print(f"   📦 24h Volume: {price_data['volume_24h']:,.0f}")
                return price_data
            else:
                error_msg = price_data.get('error', 'Unknown error')
                print(f"❌ Failed to fetch price: {error_msg}")
                return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error fetching price: {e}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

    def analyze_market_data(self, ticker, price_data, news_sentiment="Mixed market sentiment"):
        """Get AI analysis using DeepSeek"""
        print(f"3️⃣ Getting AI analysis for {ticker}...")
        try:
            analysis = self.openrouter.analyze_market_data(
                ticker=ticker,
                price_data=price_data,
                news_sentiment=news_sentiment
            )

            if analysis.get('success'):
                print(f"✅ AI Analysis completed!")
                return analysis
            else:
                error_msg = analysis.get('error', 'Unknown error')
                print(f"❌ AI analysis failed: {error_msg}")
                return {'success': False, 'error': error_msg}
        except Exception as e:
            error_msg = f"Error in AI analysis: {e}"
            print(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

    def process_query(self, user_query):
        """Process a complete crypto query from start to finish"""
        print(f"🔍 Processing query: '{user_query}'")
        print("=" * 60)

        # Step 1: Extract ticker
        ticker_result = self.extract_ticker(user_query)
        if not ticker_result['success']:
            return ticker_result

        ticker = ticker_result['ticker']

        # Step 2: Get current price
        price_data = self.get_current_price(ticker)
        if not price_data.get('success'):
            return price_data

        # Step 3: Get AI analysis
        analysis = self.analyze_market_data(ticker, price_data)

        # Combine results
        return {
            'success': True,
            'ticker': ticker,
            'price_data': price_data,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main function for testing"""
    try:
        analyzer = CryptoAnalyzer()

        # Test connections
        connections = analyzer.test_connections()

        if not all(connections.values()):
            print("❌ Some connections failed. Please check your API keys.")
            return

        # Test query processing
        test_queries = [
            "What's the price of Bitcoin?",
            "Show me Ethereum price",
            "What's happening with Solana?"
        ]

        for query in test_queries:
            print(f"\n{'='*80}")
            result = analyzer.process_query(query)
            if result['success']:
                print("✅ Query processed successfully!")
            else:
                print(f"❌ Query failed: {result.get('error')}")
            print("="*80)

    except Exception as e:
        print(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()