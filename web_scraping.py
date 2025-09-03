"""
🌐 Web Scraping Module
Extracted from crypto_trading_platform/data/web_scraping.ipynb

This module provides functions for:
1. Web scraping crypto news and data
2. Data extraction and cleaning
3. Content parsing and analysis
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

class WebScraper:
    """Web scraping utilities for crypto data"""
    
    def __init__(self):
        """Initialize the web scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_crypto_news(self, sources=None, limit=10):
        """Scrape crypto news from various sources"""
        if sources is None:
            sources = [
                'https://coindesk.com',
                'https://cointelegraph.com',
                'https://beincrypto.com'
            ]
        
        news_data = []
        
        for source in sources:
            try:
                print(f"📰 Scraping {source}...")
                response = self.session.get(source, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract headlines (this is a basic example)
                headlines = soup.find_all(['h1', 'h2', 'h3'], limit=limit)
                
                for headline in headlines:
                    if headline.text.strip():
                        news_data.append({
                            'source': source,
                            'headline': headline.text.strip(),
                            'timestamp': datetime.now().isoformat()
                        })
                
                print(f"✅ Found {len(headlines)} headlines from {source}")
                time.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                print(f"❌ Error scraping {source}: {e}")
        
        return news_data
    
    def scrape_crypto_prices(self, symbols=None):
        """Scrape crypto prices from public APIs"""
        if symbols is None:
            symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL']
        
        price_data = []
        
        try:
            # Using CoinGecko API as an example
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ','.join([f'{symbol.lower()}' for symbol in symbols]),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            for symbol_id, price_info in data.items():
                price_data.append({
                    'symbol': symbol_id.upper(),
                    'price': price_info.get('usd', 0),
                    'change_24h': price_info.get('usd_24h_change', 0),
                    'timestamp': datetime.now().isoformat()
                })
            
            print(f"✅ Scraped prices for {len(price_data)} cryptocurrencies")
            
        except Exception as e:
            print(f"❌ Error scraping prices: {e}")
        
        return price_data
    
    def extract_text_content(self, url):
        """Extract clean text content from a URL"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return {
                'success': True,
                'url': url,
                'content': text,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def scrape_social_sentiment(self, keywords=None):
        """Scrape social media sentiment (placeholder function)"""
        if keywords is None:
            keywords = ['bitcoin', 'ethereum', 'crypto']
        
        # This is a placeholder - in practice, you'd use Twitter API, Reddit API, etc.
        sentiment_data = []
        
        for keyword in keywords:
            sentiment_data.append({
                'keyword': keyword,
                'sentiment_score': 0.5,  # Placeholder
                'mention_count': 100,    # Placeholder
                'timestamp': datetime.now().isoformat()
            })
        
        print(f"📊 Collected sentiment data for {len(keywords)} keywords")
        return sentiment_data

def main():
    """Main function for testing"""
    scraper = WebScraper()
    
    print("🌐 Testing Web Scraper")
    print("=" * 50)
    
    # Test news scraping
    print("\n📰 Testing news scraping...")
    news = scraper.scrape_crypto_news(limit=5)
    print(f"Found {len(news)} news items")
    
    # Test price scraping
    print("\n💰 Testing price scraping...")
    prices = scraper.scrape_crypto_prices(['BTC', 'ETH'])
    print(f"Found {len(prices)} price entries")
    
    # Test content extraction
    print("\n📄 Testing content extraction...")
    content = scraper.extract_text_content('https://coindesk.com')
    if content['success']:
        print(f"✅ Extracted {len(content['content'])} characters")
    else:
        print(f"❌ Failed: {content['error']}")
    
    # Test sentiment scraping
    print("\n📊 Testing sentiment scraping...")
    sentiment = scraper.scrape_social_sentiment(['bitcoin'])
    print(f"Found {len(sentiment)} sentiment entries")

if __name__ == "__main__":
    main()
