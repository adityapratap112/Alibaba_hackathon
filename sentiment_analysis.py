#!/usr/bin/env python3
"""
🔍 Complete Crypto Sentiment Analysis
Single file with all sentiment analysis functionality for easy terminal testing

Usage:
    python sentiment_analysis.py
    python sentiment_analysis.py Bitcoin
    python sentiment_analysis.py Ethereum 5
"""

import os
import sys
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

# Try to import optional dependencies
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("⚠️  VADER not available. Install with: pip install vaderSentiment")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️  TextBlob not available. Install with: pip install textblob")

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️  Tavily not available. Install with: pip install tavily-python")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class CryptoSentimentAnalyzer:
    """Complete crypto sentiment analysis in a single class"""
    
    def __init__(self):
        """Initialize the sentiment analyzer"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # API keys
        self.tavily_key = os.getenv('TAVILY_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        # Initialize analyzers
        self.vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        self.tavily_client = TavilyClient(api_key=self.tavily_key) if TAVILY_AVAILABLE and self.tavily_key else None
        
        # News sources
        self.news_sources = {
            'CoinDesk': 'https://www.coindesk.com',
            'CoinTelegraph': 'https://cointelegraph.com',
            'BeInCrypto': 'https://beincrypto.com',
            'U.Today': 'https://u.today',
            'The Block': 'https://www.theblock.co'
        }
        
        print("🔍 Crypto Sentiment Analyzer Initialized")
        print(f"🔑 Tavily: {'✅' if self.tavily_client else '❌'}")
        print(f"🔑 OpenRouter: {'✅' if self.openrouter_key else '❌'}")
        print(f"📊 VADER: {'✅' if VADER_AVAILABLE else '❌'}")
        print(f"📊 TextBlob: {'✅' if TEXTBLOB_AVAILABLE else '❌'}")
    
    def search_news_tavily(self, coin_name, max_results=5):
        """Search for news using Tavily API"""
        if not self.tavily_client:
            return []
        
        try:
            query = f"{coin_name} cryptocurrency news sentiment price analysis"
            print(f"🔍 Searching Tavily: '{query}'")
            
            response = self.tavily_client.search(
                query=query,
                search_depth="basic",
                max_results=max_results
            )
            
            articles = []
            for result in response.get('results', []):
                articles.append({
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'source': 'tavily'
                })
            
            print(f"✅ Found {len(articles)} articles from Tavily")
            return articles
            
        except Exception as e:
            print(f"❌ Tavily search failed: {e}")
            return []
    
    def scrape_news_sources(self, coin_name, max_per_source=2):
        """Scrape news from crypto sources"""
        all_articles = []
        
        for source_name, source_url in self.news_sources.items():
            try:
                print(f"📰 Scraping {source_name}...")
                response = self.session.get(source_url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find headlines and articles
                headlines = soup.find_all(['h1', 'h2', 'h3', 'h4'], limit=max_per_source * 2)
                
                articles_found = 0
                for headline in headlines:
                    if articles_found >= max_per_source:
                        break
                    
                    text = headline.get_text().strip()
                    if text and coin_name.lower() in text.lower():
                        all_articles.append({
                            'title': text,
                            'content': text,
                            'url': source_url,
                            'source': source_name
                        })
                        articles_found += 1
                
                if articles_found > 0:
                    print(f"   ✅ Found {articles_found} relevant articles")
                else:
                    print(f"   ⚠️  No relevant articles found")
                
                time.sleep(1)  # Be respectful to servers
                
            except Exception as e:
                print(f"   ❌ Error scraping {source_name}: {e}")
        
        print(f"📊 Total scraped articles: {len(all_articles)}")
        return all_articles
    
    def analyze_sentiment_vader(self, text):
        """Analyze sentiment using VADER"""
        if not self.vader_analyzer:
            return None
        
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'sentiment': self._classify_sentiment(scores['compound'])
            }
        except Exception as e:
            print(f"❌ VADER analysis failed: {e}")
            return None
    
    def analyze_sentiment_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        if not TEXTBLOB_AVAILABLE:
            return None
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment': self._classify_sentiment(polarity)
            }
        except Exception as e:
            print(f"❌ TextBlob analysis failed: {e}")
            return None
    
    def analyze_sentiment_ai(self, text):
        """Analyze sentiment using AI (OpenRouter)"""
        if not self.openrouter_key:
            return None
        
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Analyze the sentiment of this crypto-related text and provide a score from -1 (very negative) to +1 (very positive):

Text: "{text[:500]}"

Respond with just a number between -1 and +1, and a brief explanation."""
            
            data = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100
            }
            
            response = self.session.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Extract score from response
                import re
                score_match = re.search(r'-?0?\.\d+|-?1\.0+|-?1|-?0', content)
                if score_match:
                    score = float(score_match.group())
                    return {
                        'score': score,
                        'sentiment': self._classify_sentiment(score),
                        'explanation': content
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ AI sentiment analysis failed: {e}")
            return None
    
    def _classify_sentiment(self, score):
        """Classify sentiment score into categories"""
        if score >= 0.1:
            return "Positive"
        elif score <= -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    def analyze_cryptocurrency(self, coin_name, max_articles=10):
        """Complete sentiment analysis for a cryptocurrency"""
        print(f"\n🔍 Starting sentiment analysis for: {coin_name}")
        print("=" * 60)
        
        # Step 1: Gather articles
        all_articles = []
        
        # Search with Tavily
        tavily_articles = self.search_news_tavily(coin_name, max_articles // 2)
        all_articles.extend(tavily_articles)
        
        # Scrape news sources
        scraped_articles = self.scrape_news_sources(coin_name, 2)
        all_articles.extend(scraped_articles)
        
        if not all_articles:
            print("❌ No articles found for analysis")
            return {
                'success': False,
                'error': 'No articles found',
                'coin_name': coin_name
            }
        
        print(f"\n📊 Analyzing {len(all_articles)} articles...")
        
        # Step 2: Analyze sentiment
        vader_scores = []
        textblob_scores = []
        ai_scores = []
        
        for i, article in enumerate(all_articles, 1):
            content = article.get('content', '') or article.get('title', '')
            if not content:
                continue
            
            print(f"   📄 Article {i}/{len(all_articles)}: {article.get('title', 'No title')[:50]}...")
            
            # VADER analysis
            vader_result = self.analyze_sentiment_vader(content)
            if vader_result:
                vader_scores.append(vader_result['compound'])
            
            # TextBlob analysis
            textblob_result = self.analyze_sentiment_textblob(content)
            if textblob_result:
                textblob_scores.append(textblob_result['polarity'])
            
            # AI analysis (only for first few articles to save API calls)
            if i <= 3:
                ai_result = self.analyze_sentiment_ai(content)
                if ai_result:
                    ai_scores.append(ai_result['score'])
        
        # Step 3: Calculate overall sentiment
        results = {
            'success': True,
            'coin_name': coin_name,
            'articles_analyzed': len(all_articles),
            'timestamp': datetime.now().isoformat()
        }
        
        if vader_scores:
            avg_vader = sum(vader_scores) / len(vader_scores)
            results['vader'] = {
                'average_score': avg_vader,
                'sentiment': self._classify_sentiment(avg_vader),
                'scores_count': len(vader_scores)
            }
        
        if textblob_scores:
            avg_textblob = sum(textblob_scores) / len(textblob_scores)
            results['textblob'] = {
                'average_score': avg_textblob,
                'sentiment': self._classify_sentiment(avg_textblob),
                'scores_count': len(textblob_scores)
            }
        
        if ai_scores:
            avg_ai = sum(ai_scores) / len(ai_scores)
            results['ai'] = {
                'average_score': avg_ai,
                'sentiment': self._classify_sentiment(avg_ai),
                'scores_count': len(ai_scores)
            }
        
        return results
    
    def print_results(self, results):
        """Print formatted results"""
        if not results['success']:
            print(f"❌ Analysis failed: {results.get('error')}")
            return
        
        print(f"\n🎯 SENTIMENT ANALYSIS RESULTS")
        print("=" * 50)
        print(f"💰 Cryptocurrency: {results['coin_name']}")
        print(f"📊 Articles Analyzed: {results['articles_analyzed']}")
        print(f"📅 Analysis Time: {results['timestamp'][:19]}")
        
        if 'vader' in results:
            vader = results['vader']
            print(f"\n📈 VADER Sentiment:")
            print(f"   Score: {vader['average_score']:.3f}")
            print(f"   Sentiment: {vader['sentiment']}")
            print(f"   Based on: {vader['scores_count']} articles")
        
        if 'textblob' in results:
            textblob = results['textblob']
            print(f"\n📈 TextBlob Sentiment:")
            print(f"   Score: {textblob['average_score']:.3f}")
            print(f"   Sentiment: {textblob['sentiment']}")
            print(f"   Based on: {textblob['scores_count']} articles")
        
        if 'ai' in results:
            ai = results['ai']
            print(f"\n🤖 AI Sentiment:")
            print(f"   Score: {ai['average_score']:.3f}")
            print(f"   Sentiment: {ai['sentiment']}")
            print(f"   Based on: {ai['scores_count']} articles")
        
        # Overall recommendation
        all_scores = []
        if 'vader' in results:
            all_scores.append(results['vader']['average_score'])
        if 'textblob' in results:
            all_scores.append(results['textblob']['average_score'])
        if 'ai' in results:
            all_scores.append(results['ai']['average_score'])
        
        if all_scores:
            overall_score = sum(all_scores) / len(all_scores)
            overall_sentiment = self._classify_sentiment(overall_score)
            
            print(f"\n🎯 OVERALL SENTIMENT:")
            print(f"   Score: {overall_score:.3f}")
            print(f"   Sentiment: {overall_sentiment}")
            
            if overall_sentiment == "Positive":
                print("   💡 Market sentiment appears bullish")
            elif overall_sentiment == "Negative":
                print("   ⚠️  Market sentiment appears bearish")
            else:
                print("   📊 Market sentiment is neutral/mixed")

def main():
    """Main function for terminal usage"""
    # Parse command line arguments
    coin_name = "Bitcoin"  # default
    max_articles = 8       # default
    
    if len(sys.argv) > 1:
        coin_name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            max_articles = int(sys.argv[2])
        except ValueError:
            print("⚠️  Invalid max_articles, using default: 8")
    
    print("🔍 Crypto Sentiment Analysis")
    print("=" * 40)
    print(f"💰 Analyzing: {coin_name}")
    print(f"📊 Max articles: {max_articles}")
    
    try:
        analyzer = CryptoSentimentAnalyzer()
        results = analyzer.analyze_cryptocurrency(coin_name, max_articles)
        analyzer.print_results(results)
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
