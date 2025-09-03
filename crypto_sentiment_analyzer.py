#!/usr/bin/env python3
"""
🤖 Crypto Sentiment Analyzer - Modular Functions
Professional-grade cryptocurrency sentiment analysis with DeepSeek AI integration

This module provides clean, reusable functions for:
- Web scraping from major crypto news sources
- Multi-method sentiment analysis (VADER, TextBlob, DeepSeek AI)
- Comprehensive market intelligence and trading insights

Usage:
    from crypto_sentiment_analyzer import CryptoSentimentAnalyzer
    
    analyzer = CryptoSentimentAnalyzer()
    results = analyzer.analyze_crypto_sentiment("Bitcoin")
    print(results['overall_sentiment'])
"""

import os
import sys
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import warnings
warnings.filterwarnings('ignore')

# Web scraping
from bs4 import BeautifulSoup

# Sentiment analysis
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Environment and AI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CryptoSentimentAnalyzer:
    """
    Professional cryptocurrency sentiment analysis with AI integration.
    
    Features:
    - Multi-source web scraping (CoinDesk, CoinTelegraph, BeInCrypto, U.Today, The Block)
    - Multi-method sentiment analysis (VADER, TextBlob, DeepSeek AI)
    - Professional market intelligence and trading recommendations
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        # API keys
        self.tavily_key = os.getenv('TAVILY_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        # Initialize sentiment analyzers
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # News sources configuration
        self.news_sources = {
            'coindesk': {
                'name': 'CoinDesk',
                'search_url': 'https://www.coindesk.com/search?s={}',
                'base_url': 'https://www.coindesk.com/'
            },
            'cointelegraph': {
                'name': 'CoinTelegraph',
                'search_url': 'https://cointelegraph.com/search?query={}',
                'base_url': 'https://cointelegraph.com/'
            },
            'beincrypto': {
                'name': 'BeInCrypto',
                'search_url': 'https://beincrypto.com/?s={}',
                'base_url': 'https://beincrypto.com/'
            },
            'utoday': {
                'name': 'U.Today',
                'search_url': 'https://u.today/search?q={}',
                'base_url': 'https://u.today/'
            },
            'theblock': {
                'name': 'The Block',
                'search_url': 'https://www.theblock.co/search?query={}',
                'base_url': 'https://www.theblock.co/'
            }
        }
        
        # Check Tavily availability
        try:
            from tavily import TavilyClient
            self.tavily_available = True
        except ImportError:
            self.tavily_available = False
    
    def search_with_tavily(self, coin_name: str, max_results: int = 10) -> List[Dict]:
        """
        Search for crypto news using Tavily API.
        
        Args:
            coin_name: Name of the cryptocurrency
            max_results: Maximum number of results to return
            
        Returns:
            List of article dictionaries
        """
        if not self.tavily_available or not self.tavily_key:
            return []
        
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_key)
            
            query = f"{coin_name} cryptocurrency news sentiment analysis price"
            
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=[
                    "coindesk.com", "cointelegraph.com", "beincrypto.com", 
                    "u.today", "theblock.co"
                ]
            )
            
            articles = []
            for result in response.get('results', []):
                articles.append({
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'source': urlparse(result.get('url', '')).netloc,
                    'method': 'tavily',
                    'timestamp': datetime.now(),
                    'relevance_score': result.get('score', 0)
                })
            
            return articles
            
        except Exception as e:
            print(f"Tavily search failed: {e}")
            return []
    
    def scrape_with_beautifulsoup(self, coin_name: str, source_name: str, max_articles: int = 5) -> List[Dict]:
        """
        Scrape articles using BeautifulSoup.
        
        Args:
            coin_name: Name of the cryptocurrency
            source_name: Name of the news source
            max_articles: Maximum number of articles to scrape
            
        Returns:
            List of article dictionaries
        """
        if source_name not in self.news_sources:
            return []
        
        source = self.news_sources[source_name]
        articles = []
        
        try:
            url = source['search_url'].format(coin_name)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic article finding
            article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['post', 'article', 'card', 'story', 'news']
            ))[:max_articles]
            
            for element in article_elements:
                try:
                    # Find title
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Find content
                    content_elems = element.find_all('p')[:3]
                    content = ' '.join([p.get_text(strip=True) for p in content_elems])
                    
                    # Find link
                    link_elem = element.find('a')
                    article_url = ''
                    if link_elem and link_elem.get('href'):
                        article_url = urljoin(source['base_url'], link_elem['href'])
                    
                    # Check relevance and quality
                    if title and len(content) > 50:
                        relevant = coin_name.lower() in (title + content).lower()
                        
                        articles.append({
                            'title': title,
                            'content': content[:600],
                            'url': article_url,
                            'source': source['name'],
                            'method': 'beautifulsoup',
                            'relevant': relevant,
                            'timestamp': datetime.now()
                        })
                        
                except Exception:
                    continue
            
            return articles
            
        except Exception as e:
            print(f"BeautifulSoup scraping failed for {source['name']}: {e}")
            return []
    
    def analyze_sentiment_vader(self, text: str) -> Dict:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        scores = self.vader_analyzer.polarity_scores(text)
        
        if scores['compound'] >= 0.05:
            sentiment = 'Positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return {
            'sentiment': sentiment,
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'method': 'vader'
        }
    
    def analyze_sentiment_textblob(self, text: str) -> Dict:
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis results
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = 'Positive'
        elif polarity < -0.1:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'
        
        return {
            'sentiment': sentiment,
            'polarity': polarity,
            'subjectivity': subjectivity,
            'method': 'textblob'
        }
    
    def analyze_sentiment_ai(self, text: str, coin_name: str) -> Dict:
        """
        Analyze sentiment using DeepSeek AI.
        
        Args:
            text: Text to analyze
            coin_name: Name of the cryptocurrency
            
        Returns:
            Dictionary with AI analysis results
        """
        if not self.openrouter_key:
            return {'error': 'OpenRouter API key missing', 'success': False}
        
        try:
            prompt = f"""Analyze sentiment of this {coin_name} news:

"{text[:600]}..."

Provide:
1. Sentiment: Positive/Negative/Neutral
2. Confidence: 1-10
3. Key indicators
4. Price impact: Bullish/Bearish/Neutral
5. Brief reasoning

Keep under 150 words."""
            
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key
            )
            
            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[
                    {"role": "system", "content": "You are a crypto sentiment expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return {
                'analysis': response.choices[0].message.content.strip(),
                'method': 'ai_deepseek',
                'success': True
            }
            
        except Exception as e:
            return {
                'error': f'AI analysis failed: {str(e)}',
                'method': 'ai_deepseek',
                'success': False
            }

    def comprehensive_ai_analysis(self, articles: List[Dict], coin_name: str) -> Dict:
        """
        Generate comprehensive AI market analysis.

        Args:
            articles: List of article dictionaries
            coin_name: Name of the cryptocurrency

        Returns:
            Dictionary with comprehensive AI analysis
        """
        if not self.openrouter_key or not articles:
            return {'error': 'OpenRouter API key missing or no articles', 'success': False}

        try:
            # Prepare data for AI analysis
            titles = [article['title'] for article in articles[:5]]
            vader_scores = []
            textblob_scores = []

            for article in articles:
                full_text = article['title'] + ' ' + article['content']
                vader_result = self.analyze_sentiment_vader(full_text)
                textblob_result = self.analyze_sentiment_textblob(full_text)
                vader_scores.append(vader_result['compound'])
                textblob_scores.append(textblob_result['polarity'])

            vader_avg = sum(vader_scores) / len(vader_scores) if vader_scores else 0
            textblob_avg = sum(textblob_scores) / len(textblob_scores) if textblob_scores else 0

            # Create comprehensive prompt
            prompt = f"""As a cryptocurrency market analyst, provide comprehensive sentiment analysis for {coin_name}:

RECENT NEWS HEADLINES:
{chr(10).join([f"• {title}" for title in titles])}

SENTIMENT SCORES:
• VADER Average: {vader_avg:.3f}
• TextBlob Average: {textblob_avg:.3f}
• Articles Analyzed: {len(articles)}

Provide:
1. **Overall Market Sentiment**: Bullish/Bearish/Neutral with confidence (1-10)
2. **Key Sentiment Drivers**: Main themes driving sentiment
3. **Price Impact Prediction**: Short-term (1-7 days) expectation
4. **Risk Assessment**: Risks and opportunities
5. **Trading Recommendation**: Buy/Hold/Sell with reasoning
6. **Market Context**: Broader crypto market comparison

Format clearly with emojis and specific confidence levels."""

            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.openrouter_key
            )

            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency market analyst with expertise in sentiment analysis and market psychology."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )

            return {
                'analysis': response.choices[0].message.content.strip(),
                'method': 'comprehensive_ai',
                'model': 'deepseek-chat-v3.1',
                'data_points': len(articles),
                'vader_avg': vader_avg,
                'textblob_avg': textblob_avg,
                'success': True
            }

        except Exception as e:
            return {
                'error': f'Comprehensive AI analysis failed: {str(e)}',
                'method': 'comprehensive_ai',
                'success': False
            }

    def collect_articles(self, coin_name: str, max_tavily: int = 5, max_bs_per_source: int = 2, fast_mode: bool = False) -> List[Dict]:
        """
        Collect articles from all sources.

        Args:
            coin_name: Name of the cryptocurrency
            max_tavily: Maximum Tavily results
            max_bs_per_source: Maximum BeautifulSoup results per source
            fast_mode: If True, only use Tavily (faster)

        Returns:
            List of all collected articles
        """
        all_articles = []

        # Tavily search (always try this first as it's most reliable)
        tavily_articles = self.search_with_tavily(coin_name, max_tavily)
        all_articles.extend(tavily_articles)

        # If fast mode or we got good Tavily results, skip BeautifulSoup
        if fast_mode or len(tavily_articles) >= 3:
            return all_articles

        # BeautifulSoup scraping (only if needed)
        successful_scrapes = 0
        for source_name in list(self.news_sources.keys())[:3]:  # Limit to first 3 sources
            try:
                articles = self.scrape_with_beautifulsoup(coin_name, source_name, max_bs_per_source)
                all_articles.extend(articles)
                if articles:
                    successful_scrapes += 1

                # Stop if we have enough data or too many failures
                if successful_scrapes >= 2 or len(all_articles) >= 8:
                    break

                time.sleep(0.5)  # Shorter delay
            except Exception:
                continue

        return all_articles

    def process_articles(self, articles: List[Dict], coin_name: str) -> List[Dict]:
        """
        Process and filter articles for relevance.

        Args:
            articles: List of raw articles
            coin_name: Name of the cryptocurrency

        Returns:
            List of processed and filtered articles
        """
        # Remove duplicates
        unique_articles = []
        seen_titles = set()

        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and len(title) > 10:
                title_key = title[:40]  # First 40 chars for dedup
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_articles.append(article)

        # Filter for relevance
        relevant_articles = []
        coin_keywords = [coin_name.lower(), coin_name.lower()[:3]]  # e.g., bitcoin, btc

        for article in unique_articles:
            text = (article.get('title', '') + ' ' + article.get('content', '')).lower()

            if any(keyword in text for keyword in coin_keywords) and len(article.get('content', '')) > 80:
                relevant_articles.append(article)

        return relevant_articles

    def analyze_crypto_sentiment(self, coin_name: str, include_ai: bool = True, verbose: bool = False, fast_mode: bool = True) -> Dict:
        """
        Complete cryptocurrency sentiment analysis.

        Args:
            coin_name: Name of the cryptocurrency
            include_ai: Whether to include AI analysis
            verbose: Whether to print progress information

        Returns:
            Dictionary with comprehensive analysis results
        """
        if verbose:
            print(f"🔍 Starting sentiment analysis for {coin_name}")

        # Collect articles
        if verbose:
            print("📰 Collecting articles from all sources...")
        all_articles = self.collect_articles(coin_name, fast_mode=fast_mode)

        # Process articles
        if verbose:
            print("🔄 Processing and filtering articles...")
        relevant_articles = self.process_articles(all_articles, coin_name)

        if not relevant_articles:
            return {
                'coin_name': coin_name,
                'error': 'No relevant articles found',
                'success': False
            }

        if verbose:
            print(f"📊 Analyzing {len(relevant_articles)} relevant articles...")

        # Analyze sentiment for each article
        all_sentiments = []
        vader_scores = []
        textblob_scores = []

        for article in relevant_articles:
            full_text = article['title'] + ' ' + article['content']

            # VADER analysis
            vader_result = self.analyze_sentiment_vader(full_text)
            vader_scores.append(vader_result['compound'])

            # TextBlob analysis
            textblob_result = self.analyze_sentiment_textblob(full_text)
            textblob_scores.append(textblob_result['polarity'])

            # Store results
            sentiment_data = {
                'article': article,
                'vader': vader_result,
                'textblob': textblob_result
            }

            all_sentiments.append(sentiment_data)

        # Calculate overall sentiment
        vader_avg = sum(vader_scores) / len(vader_scores)
        textblob_avg = sum(textblob_scores) / len(textblob_scores)

        # Count sentiment categories
        vader_sentiments = [s['vader']['sentiment'] for s in all_sentiments]
        textblob_sentiments = [s['textblob']['sentiment'] for s in all_sentiments]

        vader_counts = {s: vader_sentiments.count(s) for s in ['Positive', 'Negative', 'Neutral']}
        textblob_counts = {s: textblob_sentiments.count(s) for s in ['Positive', 'Negative', 'Neutral']}

        # Determine overall market sentiment
        if vader_avg > 0.1 and textblob_avg > 0.1:
            overall_sentiment = "Bullish"
            sentiment_strength = "Strong"
        elif vader_avg < -0.1 and textblob_avg < -0.1:
            overall_sentiment = "Bearish"
            sentiment_strength = "Strong"
        elif vader_avg > 0.05 or textblob_avg > 0.05:
            overall_sentiment = "Bullish"
            sentiment_strength = "Mild"
        elif vader_avg < -0.05 or textblob_avg < -0.05:
            overall_sentiment = "Bearish"
            sentiment_strength = "Mild"
        else:
            overall_sentiment = "Neutral"
            sentiment_strength = "Mixed"

        # Prepare results
        results = {
            'coin_name': coin_name,
            'timestamp': datetime.now(),
            'success': True,
            'data_summary': {
                'total_articles_collected': len(all_articles),
                'relevant_articles': len(relevant_articles),
                'sources_used': len(set(article.get('source', 'Unknown') for article in relevant_articles))
            },
            'sentiment_scores': {
                'vader_average': vader_avg,
                'textblob_average': textblob_avg,
                'vader_distribution': vader_counts,
                'textblob_distribution': textblob_counts
            },
            'overall_sentiment': overall_sentiment,
            'sentiment_strength': sentiment_strength,
            'articles': all_sentiments,
            'most_positive_article': max(all_sentiments, key=lambda x: x['vader']['compound']) if all_sentiments else None,
            'most_negative_article': min(all_sentiments, key=lambda x: x['vader']['compound']) if all_sentiments else None
        }

        # Add AI analysis if requested
        if include_ai and self.openrouter_key:
            if verbose:
                print("🤖 Generating AI analysis...")
            ai_analysis = self.comprehensive_ai_analysis(relevant_articles, coin_name)
            results['ai_analysis'] = ai_analysis

        return results

    def get_quick_sentiment(self, coin_name: str) -> str:
        """
        Get quick sentiment classification.

        Args:
            coin_name: Name of the cryptocurrency

        Returns:
            Simple sentiment string (Bullish/Bearish/Neutral)
        """
        results = self.analyze_crypto_sentiment(coin_name, include_ai=False, verbose=False)
        if results.get('success'):
            return f"{results['sentiment_strength']} {results['overall_sentiment']}"
        else:
            return "Analysis Failed"

    def get_trading_signal(self, coin_name: str) -> Dict:
        """
        Get trading signal based on sentiment analysis.

        Args:
            coin_name: Name of the cryptocurrency

        Returns:
            Dictionary with trading signal and confidence
        """
        results = self.analyze_crypto_sentiment(coin_name, include_ai=True, verbose=False)

        if not results.get('success'):
            return {'signal': 'HOLD', 'confidence': 0, 'reason': 'Analysis failed'}

        vader_avg = results['sentiment_scores']['vader_average']
        textblob_avg = results['sentiment_scores']['textblob_average']

        # Determine trading signal
        if vader_avg > 0.2 and textblob_avg > 0.2:
            signal = 'BUY'
            confidence = min(90, int((vader_avg + textblob_avg) * 50 + 50))
        elif vader_avg < -0.2 and textblob_avg < -0.2:
            signal = 'SELL'
            confidence = min(90, int(abs(vader_avg + textblob_avg) * 50 + 50))
        elif vader_avg > 0.1 or textblob_avg > 0.1:
            signal = 'BUY'
            confidence = min(70, int((abs(vader_avg) + abs(textblob_avg)) * 40 + 30))
        elif vader_avg < -0.1 or textblob_avg < -0.1:
            signal = 'SELL'
            confidence = min(70, int((abs(vader_avg) + abs(textblob_avg)) * 40 + 30))
        else:
            signal = 'HOLD'
            confidence = 50

        return {
            'signal': signal,
            'confidence': confidence,
            'sentiment': results['overall_sentiment'],
            'strength': results['sentiment_strength'],
            'reason': f"Based on {results['data_summary']['relevant_articles']} articles from {results['data_summary']['sources_used']} sources"
        }
