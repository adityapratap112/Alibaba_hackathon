#!/usr/bin/env python3
"""
🔍 Crypto Sentiment Analysis - Web Scraping Script
Deep Sentiment Analysis from Major Crypto News Sources

Sources: CoinDesk, CoinTelegraph, BeInCrypto, U.Today, The Block
Tools: Tavily API, BeautifulSoup, Selenium, AI Analysis, VADER & TextBlob

Run this script and enter a cryptocurrency name for comprehensive sentiment analysis.
"""

import os
import sys
import requests
import time
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin, urlparse
import warnings
warnings.filterwarnings('ignore')

# Add parent directory
sys.path.append('/Users/aditya/PycharmProjects/PAlibaba_hackathon')

# Web scraping
from bs4 import BeautifulSoup

# Sentiment analysis
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from openrouter_config import openrouter_config
from dotenv import load_dotenv

load_dotenv()

# Try Tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
    print("✅ Tavily available")
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️  Tavily not available - install with: pip install tavily-python")

# Initialize
vader_analyzer = SentimentIntensityAnalyzer()

# Configuration
NEWS_SOURCES = {
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

# Check API keys
tavily_key = os.getenv('TAVILY_API_KEY')
openrouter_key = os.getenv('OPENROUTER_API_KEY')

def search_with_tavily(coin_name: str, max_results: int = 10) -> List[Dict]:
    """Search using Tavily API."""
    if not TAVILY_AVAILABLE or not tavily_key:
        print("⚠️  Tavily not available")
        return []
    
    try:
        client = TavilyClient(api_key=tavily_key)
        query = f"{coin_name} cryptocurrency news sentiment analysis price"
        
        print(f"🔍 Searching: '{query}'")
        
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
                'timestamp': datetime.now()
            })
        
        print(f"✅ Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"❌ Tavily failed: {e}")
        return []

def scrape_with_bs(coin_name: str, source_name: str) -> List[Dict]:
    """Scrape using BeautifulSoup."""
    if source_name not in NEWS_SOURCES:
        return []
    
    source = NEWS_SOURCES[source_name]
    articles = []
    
    try:
        url = source['search_url'].format(coin_name)
        print(f"🍲 Scraping {source['name']}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Generic article finding
        article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['post', 'article', 'card', 'story', 'news']
        ))[:5]
        
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
                
                # Check relevance
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
        
        print(f"   ✅ Found {len(articles)} articles")
        return articles
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return []

def analyze_sentiment_vader(text: str) -> Dict:
    """VADER sentiment analysis."""
    scores = vader_analyzer.polarity_scores(text)
    
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
        'neutral': scores['neu']
    }

def analyze_sentiment_textblob(text: str) -> Dict:
    """TextBlob sentiment analysis."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        sentiment = 'Positive'
    elif polarity < -0.1:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    
    return {
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': blob.sentiment.subjectivity
    }

def analyze_sentiment_ai(text: str, coin_name: str) -> Dict:
    """AI sentiment analysis using DeepSeek."""
    if not openrouter_key:
        return {'error': 'OpenRouter API key missing'}
    
    try:
        prompt = f"""Analyze sentiment of this {coin_name} news:

"{text[:600]}..."

Provide:
1. Sentiment: Positive/Negative/Neutral
2. Confidence: 1-10
3. Key indicators
4. Price impact: Bullish/Bearish/Neutral

Keep under 100 words."""
        
        from openai import OpenAI
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_key
        )
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3.1:free",
            messages=[
                {"role": "system", "content": "You are a crypto sentiment expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        return {
            'analysis': response.choices[0].message.content.strip(),
            'success': True
        }
        
    except Exception as e:
        return {'error': f'AI analysis failed: {str(e)}'}

def main():
    """Main function to run the sentiment analysis."""
    print("🔍 Crypto Sentiment Analysis - Web Scraping")
    print("=" * 60)
    
    # Check setup
    print(f"📰 {len(NEWS_SOURCES)} news sources configured")
    print(f"🔑 Tavily: {'✅' if tavily_key else '❌'}")
    print(f"🔑 OpenRouter: {'✅' if openrouter_key else '❌'}")
    
    # Get user input
    coin_name = input("\n🪙 Enter cryptocurrency (e.g., Bitcoin, Ethereum): ").strip()
    
    if not coin_name:
        coin_name = "Bitcoin"
        print(f"Using default: {coin_name}")
    
    print(f"\n🔍 Starting sentiment analysis for: {coin_name}")
    print("=" * 60)
    
    all_articles = []
    
    # Step 1: Tavily search
    print("\n🔍 STEP 1: Tavily Search")
    print("-" * 30)
    
    tavily_articles = search_with_tavily(coin_name, max_results=8)
    all_articles.extend(tavily_articles)
    
    if tavily_articles:
        print("\nTop results:")
        for i, article in enumerate(tavily_articles[:3], 1):
            print(f"{i}. {article['title'][:70]}...")
            print(f"   Source: {article['source']}")
    
    # Step 2: BeautifulSoup scraping
    print("\n🍲 STEP 2: BeautifulSoup Scraping")
    print("-" * 30)
    
    bs_articles = []
    for source_name in NEWS_SOURCES.keys():
        articles = scrape_with_bs(coin_name, source_name)
        bs_articles.extend(articles)
        time.sleep(1)  # Be respectful
    
    all_articles.extend(bs_articles)
    print(f"\n📊 BeautifulSoup total: {len(bs_articles)} articles")
    
    # Step 3: Process articles
    print("\n🔄 STEP 3: Processing Articles")
    print("-" * 30)
    
    # Remove duplicates
    unique_articles = []
    seen_titles = set()
    
    for article in all_articles:
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
    
    print(f"📊 Results:")
    print(f"   • Total scraped: {len(all_articles)}")
    print(f"   • After dedup: {len(unique_articles)}")
    print(f"   • Relevant to {coin_name}: {len(relevant_articles)}")
    
    # Show breakdown
    sources = {}
    for article in relevant_articles:
        source = article.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📰 By source:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {source}: {count}")
    
    if not relevant_articles:
        print("❌ No relevant articles found for analysis")
        return

    # Step 4: Sentiment analysis
    print("\n🧠 STEP 4: Sentiment Analysis")
    print("-" * 30)

    print(f"Analyzing {len(relevant_articles)} articles...\n")

    all_sentiments = []

    for i, article in enumerate(relevant_articles[:10], 1):  # Limit to 10 for demo
        print(f"📄 Article {i}: {article['title'][:60]}...")
        print(f"   Source: {article['source']}")

        # Combine title and content for analysis
        full_text = article['title'] + ' ' + article['content']

        # VADER analysis
        vader_result = analyze_sentiment_vader(full_text)
        print(f"   🎯 VADER: {vader_result['sentiment']} ({vader_result['compound']:.2f})")

        # TextBlob analysis
        textblob_result = analyze_sentiment_textblob(full_text)
        print(f"   📊 TextBlob: {textblob_result['sentiment']} ({textblob_result['polarity']:.2f})")

        # AI analysis (for first 3 articles to save API calls)
        if i <= 3 and openrouter_key:
            ai_result = analyze_sentiment_ai(full_text, coin_name)
            if ai_result.get('success'):
                print(f"   🤖 AI Analysis: {ai_result['analysis'][:80]}...")
            else:
                print(f"   🤖 AI Analysis: {ai_result.get('error', 'Failed')}")

        # Store results
        sentiment_data = {
            'article': article,
            'vader': vader_result,
            'textblob': textblob_result
        }

        if i <= 3 and openrouter_key:
            sentiment_data['ai'] = ai_result

        all_sentiments.append(sentiment_data)
        print()

    # Step 5: Generate summary
    print("\n📊 STEP 5: Comprehensive Sentiment Summary")
    print("=" * 60)

    if all_sentiments:
        # Calculate overall sentiment scores
        vader_scores = [s['vader']['compound'] for s in all_sentiments]
        textblob_scores = [s['textblob']['polarity'] for s in all_sentiments]

        vader_avg = sum(vader_scores) / len(vader_scores)
        textblob_avg = sum(textblob_scores) / len(textblob_scores)

        # Count sentiment categories
        vader_sentiments = [s['vader']['sentiment'] for s in all_sentiments]
        textblob_sentiments = [s['textblob']['sentiment'] for s in all_sentiments]

        vader_counts = {s: vader_sentiments.count(s) for s in ['Positive', 'Negative', 'Neutral']}
        textblob_counts = {s: textblob_sentiments.count(s) for s in ['Positive', 'Negative', 'Neutral']}

        print(f"🪙 **{coin_name} Sentiment Analysis Results**\n")

        print(f"📈 **Overall Sentiment Scores:**")
        print(f"   • VADER Average: {vader_avg:.3f} ({'Positive' if vader_avg > 0.05 else 'Negative' if vader_avg < -0.05 else 'Neutral'})")
        print(f"   • TextBlob Average: {textblob_avg:.3f} ({'Positive' if textblob_avg > 0.1 else 'Negative' if textblob_avg < -0.1 else 'Neutral'})")

        print(f"\n📊 **Sentiment Distribution:**")
        print(f"   VADER: {vader_counts['Positive']} Positive, {vader_counts['Negative']} Negative, {vader_counts['Neutral']} Neutral")
        print(f"   TextBlob: {textblob_counts['Positive']} Positive, {textblob_counts['Negative']} Negative, {textblob_counts['Neutral']} Neutral")

        # Determine overall market sentiment
        if vader_avg > 0.1 and textblob_avg > 0.1:
            overall_sentiment = "🟢 **BULLISH** - Strong positive sentiment"
        elif vader_avg < -0.1 and textblob_avg < -0.1:
            overall_sentiment = "🔴 **BEARISH** - Strong negative sentiment"
        elif vader_avg > 0.05 or textblob_avg > 0.05:
            overall_sentiment = "🟡 **CAUTIOUSLY OPTIMISTIC** - Mild positive sentiment"
        elif vader_avg < -0.05 or textblob_avg < -0.05:
            overall_sentiment = "🟠 **CAUTIOUSLY PESSIMISTIC** - Mild negative sentiment"
        else:
            overall_sentiment = "⚪ **NEUTRAL** - Mixed or neutral sentiment"

        print(f"\n🎯 **Overall Market Sentiment for {coin_name}:**")
        print(f"   {overall_sentiment}")

        print(f"\n📰 **Source Breakdown:**")
        source_sentiments = {}
        for sentiment_data in all_sentiments:
            source = sentiment_data['article']['source']
            vader_sentiment = sentiment_data['vader']['sentiment']
            if source not in source_sentiments:
                source_sentiments[source] = []
            source_sentiments[source].append(vader_sentiment)

        for source, sentiments in source_sentiments.items():
            pos = sentiments.count('Positive')
            neg = sentiments.count('Negative')
            neu = sentiments.count('Neutral')
            print(f"   • {source}: {pos}+ {neg}- {neu}○")

        print(f"\n🔍 **Key Insights:**")
        print(f"   • Analyzed {len(all_sentiments)} articles from {len(source_sentiments)} sources")
        print(f"   • Data collected: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"   • Sentiment range: {min(vader_scores):.3f} to {max(vader_scores):.3f}")

        # Show most positive and negative articles
        if len(all_sentiments) > 1:
            most_positive = max(all_sentiments, key=lambda x: x['vader']['compound'])
            most_negative = min(all_sentiments, key=lambda x: x['vader']['compound'])

            print(f"\n📈 **Most Positive Article:**")
            print(f"   {most_positive['article']['title'][:80]}...")
            print(f"   Score: {most_positive['vader']['compound']:.3f} | Source: {most_positive['article']['source']}")

            print(f"\n📉 **Most Negative Article:**")
            print(f"   {most_negative['article']['title'][:80]}...")
            print(f"   Score: {most_negative['vader']['compound']:.3f} | Source: {most_negative['article']['source']}")

    print(f"\n🎉 **Sentiment Analysis Complete for {coin_name}!**")

if __name__ == "__main__":
    main()
