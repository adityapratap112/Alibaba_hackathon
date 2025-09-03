"""
Binance API Integration for Crypto Trading Platform

This module provides functions to fetch current prices and historical data
from Binance API for cryptocurrency trading analysis.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BinanceAPI:
    """Binance API client for fetching cryptocurrency data."""
    
    def __init__(self):
        """Initialize Binance API client."""
        self.base_url = "https://api.binance.com/api/v3"
        self.api_key = os.getenv('BINANCE_API_KEY')  # Optional for public endpoints
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')  # Optional for public endpoints
        
        # Common trading pairs
        self.common_pairs = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT', 
            'BNB': 'BNBUSDT',
            'ADA': 'ADAUSDT',
            'SOL': 'SOLUSDT',
            'DOT': 'DOTUSDT',
            'LINK': 'LINKUSDT',
            'MATIC': 'MATICUSDT',
            'AVAX': 'AVAXUSDT',
            'ATOM': 'ATOMUSDT'
        }
    
    def get_trading_pair(self, ticker: str) -> str:
        """
        Convert ticker to Binance trading pair format.
        
        Args:
            ticker (str): Cryptocurrency ticker (e.g., 'BTC')
            
        Returns:
            str: Binance trading pair (e.g., 'BTCUSDT')
        """
        ticker = ticker.upper()
        
        # Check if it's already a trading pair
        if ticker.endswith('USDT'):
            return ticker
        
        # Check common pairs
        if ticker in self.common_pairs:
            return self.common_pairs[ticker]
        
        # Default to USDT pair
        return f"{ticker}USDT"
    
    def get_current_price(self, ticker: str) -> Dict:
        """
        Get current price for a cryptocurrency.
        
        Args:
            ticker (str): Cryptocurrency ticker
            
        Returns:
            Dict: Current price data
        """
        trading_pair = self.get_trading_pair(ticker)
        
        try:
            # Get 24hr ticker statistics
            url = f"{self.base_url}/ticker/24hr"
            params = {'symbol': trading_pair}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'ticker': ticker,
                'trading_pair': trading_pair,
                'current_price': float(data['lastPrice']),
                'price_change_24h': float(data['priceChangePercent']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'volume_24h': float(data['volume']),
                'timestamp': datetime.now(),
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'ticker': ticker,
                'error': f"API request failed: {str(e)}",
                'success': False
            }
        except (KeyError, ValueError) as e:
            return {
                'ticker': ticker,
                'error': f"Data parsing failed: {str(e)}",
                'success': False
            }
    
    def get_historical_data(self, ticker: str, interval: str = '1d', days: int = 30) -> Dict:
        """
        Get historical price data for a cryptocurrency.
        
        Args:
            ticker (str): Cryptocurrency ticker
            interval (str): Kline interval (1m, 5m, 1h, 1d, etc.)
            days (int): Number of days of historical data
            
        Returns:
            Dict: Historical price data
        """
        trading_pair = self.get_trading_pair(ticker)
        
        try:
            # Calculate start time
            end_time = int(time.time() * 1000)
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            url = f"{self.base_url}/klines"
            params = {
                'symbol': trading_pair,
                'interval': interval,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1000
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process data without pandas
            processed_data = []
            for i, row in enumerate(data):
                processed_row = {
                    'timestamp': datetime.fromtimestamp(int(row[0]) / 1000),
                    'open': float(row[1]),
                    'high': float(row[2]),
                    'low': float(row[3]),
                    'close': float(row[4]),
                    'volume': float(row[5])
                }

                # Calculate price change
                if i > 0:
                    prev_close = float(data[i-1][4])
                    processed_row['price_change'] = ((processed_row['close'] / prev_close) - 1) * 100
                else:
                    processed_row['price_change'] = 0.0

                processed_data.append(processed_row)

            # Calculate simple moving averages
            for i, row in enumerate(processed_data):
                # 7-day SMA
                if i >= 6:
                    sma_7_sum = sum(processed_data[j]['close'] for j in range(i-6, i+1))
                    row['sma_7'] = sma_7_sum / 7
                else:
                    row['sma_7'] = row['close']

                # 30-day SMA (if enough data)
                if i >= 29:
                    sma_30_sum = sum(processed_data[j]['close'] for j in range(i-29, i+1))
                    row['sma_30'] = sma_30_sum / 30
                else:
                    row['sma_30'] = row['close']
            
            # Calculate summary statistics
            closes = [row['close'] for row in processed_data]
            lows = [row['low'] for row in processed_data]
            highs = [row['high'] for row in processed_data]
            volumes = [row['volume'] for row in processed_data]

            return {
                'ticker': ticker,
                'trading_pair': trading_pair,
                'interval': interval,
                'days': days,
                'data': processed_data,
                'summary': {
                    'total_records': len(processed_data),
                    'date_range': f"{processed_data[0]['timestamp']} to {processed_data[-1]['timestamp']}",
                    'price_range': f"${min(lows):.2f} - ${max(highs):.2f}",
                    'avg_volume': sum(volumes) / len(volumes),
                    'total_return': ((closes[-1] / closes[0]) - 1) * 100 if len(closes) > 1 else 0
                },
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'ticker': ticker,
                'error': f"API request failed: {str(e)}",
                'success': False
            }
        except Exception as e:
            return {
                'ticker': ticker,
                'error': f"Data processing failed: {str(e)}",
                'success': False
            }
    
    def get_multiple_prices(self, tickers: List[str]) -> Dict:
        """
        Get current prices for multiple cryptocurrencies.
        
        Args:
            tickers (List[str]): List of cryptocurrency tickers
            
        Returns:
            Dict: Current prices for all tickers
        """
        results = {}
        
        for ticker in tickers:
            price_data = self.get_current_price(ticker)
            results[ticker] = price_data
            time.sleep(0.1)  # Rate limiting
        
        return {
            'results': results,
            'timestamp': datetime.now(),
            'total_tickers': len(tickers),
            'successful': sum(1 for r in results.values() if r.get('success', False))
        }
    
    def test_connection(self) -> bool:
        """Test connection to Binance API."""
        try:
            url = f"{self.base_url}/ping"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

# Global API instance
binance_api = BinanceAPI()

def test_binance_integration():
    """Test Binance API integration."""
    print("🧪 Testing Binance API Integration")
    print("-" * 40)
    
    # Test connection
    if binance_api.test_connection():
        print("✅ Binance API connection successful!")
    else:
        print("❌ Binance API connection failed!")
        return False
    
    # Test current price
    print("\n📊 Testing current price fetch:")
    btc_price = binance_api.get_current_price('BTC')
    if btc_price.get('success'):
        print(f"✅ BTC Price: ${btc_price['current_price']:,.2f} ({btc_price['price_change_24h']:+.2f}%)")
    else:
        print(f"❌ Failed to get BTC price: {btc_price.get('error')}")
    
    # Test historical data
    print("\n📈 Testing historical data fetch:")
    btc_history = binance_api.get_historical_data('BTC', days=7)
    if btc_history.get('success'):
        print(f"✅ BTC Historical Data: {btc_history['summary']['total_records']} records")
        print(f"   Date Range: {btc_history['summary']['date_range']}")
        print(f"   Total Return: {btc_history['summary']['total_return']:+.2f}%")
    else:
        print(f"❌ Failed to get BTC history: {btc_history.get('error')}")
    
    return True

if __name__ == "__main__":
    test_binance_integration()
