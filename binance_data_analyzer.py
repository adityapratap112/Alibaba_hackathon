#!/usr/bin/env python3
"""
🚀 Binance Data Analyzer - Modular Functions
Professional cryptocurrency data analysis with Binance API and DeepSeek AI

This module provides clean, reusable functions for:
- Cryptocurrency ticker extraction from natural language queries
- Real-time price data fetching from Binance API
- AI-powered market analysis using DeepSeek
- Historical data analysis and visualization
- Complete query processing pipeline

Usage:
    from binance_data_analyzer import BinanceDataAnalyzer
    
    analyzer = BinanceDataAnalyzer()
    result = analyzer.process_crypto_query("What's the price of Bitcoin?")
    print(result['analysis'])
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from openrouter_config import openrouter_config
from binance_api import binance_api

class BinanceDataAnalyzer:
    """
    Professional cryptocurrency data analysis with Binance API and AI integration.
    
    Features:
    - Natural language query processing
    - Real-time price data from Binance API
    - AI-powered market analysis using DeepSeek
    - Historical data analysis and visualization
    - Complete data pipeline automation
    """
    
    def __init__(self):
        """Initialize the Binance data analyzer."""
        self.openrouter_config = openrouter_config
        self.binance_api = binance_api
    
    def extract_ticker_from_query(self, user_query: str) -> Dict:
        """
        Extract cryptocurrency ticker from natural language query.
        
        Args:
            user_query: Natural language query about cryptocurrency
            
        Returns:
            Dictionary with ticker extraction results
        """
        try:
            result = self.openrouter_config.extract_crypto_ticker(user_query)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'Ticker extraction failed: {str(e)}',
                'ticker': None
            }
    
    def get_current_price_data(self, ticker: str) -> Dict:
        """
        Fetch current price data from Binance API.
        
        Args:
            ticker: Cryptocurrency ticker symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary with current price data
        """
        try:
            result = self.binance_api.get_current_price(ticker)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'Price data fetch failed: {str(e)}',
                'current_price': None
            }
    
    def get_ai_market_analysis(self, ticker: str, price_data: Dict, news_sentiment: str = "Mixed market sentiment") -> Dict:
        """
        Get AI-powered market analysis using DeepSeek.
        
        Args:
            ticker: Cryptocurrency ticker symbol
            price_data: Current price data dictionary
            news_sentiment: Optional news sentiment context
            
        Returns:
            Dictionary with AI analysis results
        """
        try:
            result = self.openrouter_config.analyze_market_data(
                ticker=ticker,
                price_data=price_data,
                news_sentiment=news_sentiment
            )
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'AI analysis failed: {str(e)}',
                'analysis': None
            }
    
    def get_historical_data(self, ticker: str, interval: str = '1d', days: int = 7) -> Dict:
        """
        Fetch historical price data from Binance API.
        
        Args:
            ticker: Cryptocurrency ticker symbol
            interval: Data interval (1d, 1h, etc.)
            days: Number of days of historical data
            
        Returns:
            Dictionary with historical data and summary
        """
        try:
            result = self.binance_api.get_historical_data(ticker, interval=interval, days=days)
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'Historical data fetch failed: {str(e)}',
                'data': None
            }
    
    def process_crypto_query(self, user_query: str, include_historical: bool = False, historical_days: int = 7) -> Dict:
        """
        Complete cryptocurrency query processing pipeline.
        
        Args:
            user_query: Natural language query about cryptocurrency
            include_historical: Whether to include historical data analysis
            historical_days: Number of days for historical data
            
        Returns:
            Dictionary with complete analysis results
        """
        if not user_query.strip():
            return {
                'success': False,
                'error': 'Empty query provided',
                'ticker': None,
                'price_data': None,
                'ai_analysis': None
            }
        
        try:
            # Step 1: Extract ticker using DeepSeek
            ticker_result = self.extract_ticker_from_query(user_query)
            
            if not ticker_result.get('success'):
                return {
                    'success': False,
                    'error': f"Could not extract cryptocurrency from query: {ticker_result.get('error')}",
                    'ticker': None,
                    'price_data': None,
                    'ai_analysis': None
                }
            
            ticker = ticker_result['ticker']
            
            # Step 2: Fetch current price from Binance
            price_data = self.get_current_price_data(ticker)
            
            if not price_data.get('success'):
                return {
                    'success': False,
                    'error': f"Could not fetch price for {ticker}: {price_data.get('error')}",
                    'ticker': ticker,
                    'price_data': None,
                    'ai_analysis': None
                }
            
            # Step 3: Get AI analysis
            ai_analysis = self.get_ai_market_analysis(ticker, price_data)
            
            # Step 4: Get historical data if requested
            historical_data = None
            if include_historical:
                historical_data = self.get_historical_data(ticker, days=historical_days)
            
            # Compile results
            result = {
                'success': True,
                'timestamp': datetime.now(),
                'query': user_query,
                'ticker': ticker,
                'price_data': price_data,
                'ai_analysis': ai_analysis,
                'historical_data': historical_data if include_historical else None
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Query processing failed: {str(e)}',
                'ticker': None,
                'price_data': None,
                'ai_analysis': None
            }
    
    def get_price_summary(self, ticker: str, price_data: Dict) -> Dict:
        """
        Get formatted price summary data.

        Args:
            ticker: Cryptocurrency ticker symbol
            price_data: Current price data dictionary

        Returns:
            Dictionary with formatted price summary
        """
        if not price_data.get('success'):
            return {'success': False, 'error': 'Invalid price data'}

        try:
            summary_data = {
                'ticker': ticker,
                'current_price': f"${price_data['current_price']:,.2f}",
                'price_change_24h': f"{price_data['price_change_24h']:+.2f}%",
                'high_24h': f"${price_data['high_24h']:,.2f}",
                'low_24h': f"${price_data['low_24h']:,.2f}",
                'volume_24h': f"{price_data['volume_24h']:,.0f}",
                'raw_data': price_data
            }

            return {
                'success': True,
                'summary': summary_data
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Summary creation failed: {str(e)}'
            }
    
    def format_analysis_report(self, analysis_result: Dict) -> str:
        """
        Format analysis results into a readable report.
        
        Args:
            analysis_result: Complete analysis results dictionary
            
        Returns:
            Formatted string report
        """
        if not analysis_result.get('success'):
            return f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}"
        
        ticker = analysis_result['ticker']
        price_data = analysis_result['price_data']
        ai_analysis = analysis_result['ai_analysis']
        
        report = f"""
🎯 **Cryptocurrency Analysis Report**

**Query:** {analysis_result['query']}
**Cryptocurrency:** {ticker}
**Analysis Time:** {analysis_result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

📊 **Current Market Data:**
• Current Price: ${price_data['current_price']:,.2f}
• 24h Change: {price_data['price_change_24h']:+.2f}%
• 24h High/Low: ${price_data['high_24h']:,.2f} / ${price_data['low_24h']:,.2f}
• 24h Volume: {price_data['volume_24h']:,.0f}

🤖 **AI Market Analysis:**
{ai_analysis.get('analysis', 'Analysis not available') if ai_analysis.get('success') else f"Analysis failed: {ai_analysis.get('error', 'Unknown error')}"}

📈 **Data Sources:**
• Price Data: Binance API
• AI Analysis: DeepSeek (via OpenRouter)
• Real-time Updates: Live market data
        """
        
        # Add historical data summary if available
        if analysis_result.get('historical_data') and analysis_result['historical_data'].get('success'):
            hist_summary = analysis_result['historical_data']['summary']
            report += f"""

📊 **Historical Data Summary:**
• Records: {hist_summary['total_records']}
• Date Range: {hist_summary['date_range']}
• Price Range: {hist_summary['price_range']}
• Total Return: {hist_summary['total_return']:+.2f}%
• Average Volume: {hist_summary['avg_volume']:,.0f}
        """
        
        return report
    
    def get_quick_price(self, ticker_or_query: str) -> str:
        """
        Get quick price information for a cryptocurrency.
        
        Args:
            ticker_or_query: Either a ticker symbol or natural language query
            
        Returns:
            Quick price summary string
        """
        # Try as direct ticker first
        if len(ticker_or_query) <= 10 and ticker_or_query.isupper():
            price_data = self.get_current_price_data(ticker_or_query)
            if price_data.get('success'):
                return f"{ticker_or_query}: ${price_data['current_price']:,.2f} ({price_data['price_change_24h']:+.2f}%)"
        
        # Process as natural language query
        result = self.process_crypto_query(ticker_or_query)
        if result.get('success'):
            ticker = result['ticker']
            price_data = result['price_data']
            return f"{ticker}: ${price_data['current_price']:,.2f} ({price_data['price_change_24h']:+.2f}%)"
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
