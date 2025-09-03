"""
OpenRouter Configuration for Crypto Trading Platform

This module provides configuration and utilities for integrating with OpenRouter
using DeepSeek models for our cryptocurrency trading platform.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, List, Optional
import json

# Load environment variables
load_dotenv()

class OpenRouterConfig:
    """Configuration class for OpenRouter integration."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Initialize OpenAI client with OpenRouter endpoint
        if self.api_key:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            self.client = None
            print("⚠️  Warning: OPENROUTER_API_KEY not found in environment variables")
    
    # Model configurations for crypto trading
    MODELS = {
        'ticker_extraction': {
            'model': 'deepseek/deepseek-chat-v3.1:free',
            'description': 'Free DeepSeek model for extracting crypto tickers from user queries',
            'cost': 'Free',
            'max_tokens': 4000,
            'use_case': 'Extract cryptocurrency symbols from natural language'
        },
        
        'market_analysis': {
            'model': 'deepseek/deepseek-chat-v3.1:free',
            'description': 'Free DeepSeek model for market analysis and insights',
            'cost': 'Free',
            'max_tokens': 4000,
            'use_case': 'Analyze market trends and provide trading insights'
        }
    }
    
    def extract_crypto_ticker(self, user_query: str) -> Dict:
        """
        Extract cryptocurrency ticker from user query using DeepSeek.
        
        Args:
            user_query (str): User's natural language query
            
        Returns:
            Dict: Contains extracted ticker and confidence
        """
        if not self.client:
            return {"error": "OpenRouter client not initialized"}
        
        system_prompt = """You are a cryptocurrency ticker extraction expert. 
        Extract the cryptocurrency ticker symbol from the user's query.
        
        Rules:
        1. Return ONLY the ticker symbol in uppercase (e.g., BTC, ETH, ADA)
        2. If multiple tickers mentioned, return the primary one
        3. If no clear ticker found, return "UNKNOWN"
        4. Common mappings: Bitcoin=BTC, Ethereum=ETH, Cardano=ADA, Solana=SOL
        
        Respond with ONLY the ticker symbol, nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.MODELS['ticker_extraction']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            ticker = response.choices[0].message.content.strip().upper()
            
            return {
                "ticker": ticker,
                "original_query": user_query,
                "success": ticker != "UNKNOWN",
                "model_used": self.MODELS['ticker_extraction']['model']
            }
            
        except Exception as e:
            return {
                "error": f"Failed to extract ticker: {str(e)}",
                "ticker": "UNKNOWN",
                "success": False
            }
    
    def analyze_market_data(self, ticker: str, price_data: Dict, news_sentiment: str = "") -> Dict:
        """
        Analyze market data and provide insights using DeepSeek.
        
        Args:
            ticker (str): Cryptocurrency ticker
            price_data (Dict): Current and historical price data
            news_sentiment (str): Optional news sentiment summary
            
        Returns:
            Dict: Market analysis and recommendations
        """
        if not self.client:
            return {"error": "OpenRouter client not initialized"}
        
        # Prepare market data summary
        current_price = price_data.get('current_price', 'N/A')
        price_change_24h = price_data.get('price_change_24h', 'N/A')
        
        analysis_prompt = f"""Analyze the following cryptocurrency data and provide brief trading insights:

Cryptocurrency: {ticker}
Current Price: ${current_price}
24h Price Change: {price_change_24h}%
News Sentiment: {news_sentiment if news_sentiment else "No sentiment data available"}

Provide a brief analysis including:
1. Price trend assessment
2. Risk level (Low/Medium/High)
3. Short-term outlook (Bullish/Bearish/Neutral)
4. One key insight

Keep response under 150 words."""

        try:
            response = self.client.chat.completions.create(
                model=self.MODELS['market_analysis']['model'],
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency market analyst. Provide concise, actionable insights."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "ticker": ticker,
                "analysis": analysis,
                "timestamp": price_data.get('timestamp'),
                "model_used": self.MODELS['market_analysis']['model'],
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Failed to analyze market data: {str(e)}",
                "success": False
            }
    
    def test_connection(self) -> bool:
        """Test connection to OpenRouter."""
        if not self.client:
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.MODELS['ticker_extraction']['model'],
                messages=[
                    {"role": "user", "content": "Test connection - respond with 'OK'"}
                ],
                max_tokens=5
            )
            
            return "OK" in response.choices[0].message.content
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Global configuration instance
openrouter_config = OpenRouterConfig()

def test_ticker_extraction():
    """Test ticker extraction functionality."""
    test_queries = [
        "What's the current price of Bitcoin?",
        "Show me ETH price",
        "How is Cardano performing today?",
        "Tell me about Solana",
        "What about MATIC?"
    ]
    
    print("🧪 Testing Ticker Extraction:")
    print("-" * 40)
    
    for query in test_queries:
        result = openrouter_config.extract_crypto_ticker(query)
        if result.get('success'):
            print(f"✅ '{query}' → {result['ticker']}")
        else:
            print(f"❌ '{query}' → {result.get('ticker', 'ERROR')}")

if __name__ == "__main__":
    print("🤖 OpenRouter Configuration for Crypto Trading Platform")
    print("=" * 60)
    
    # Test connection
    if openrouter_config.test_connection():
        print("✅ OpenRouter connection successful!")
        print("\n🔧 Testing ticker extraction...")
        test_ticker_extraction()
    else:
        print("❌ OpenRouter connection failed!")
        print("Please check your OPENROUTER_API_KEY in .env file")
