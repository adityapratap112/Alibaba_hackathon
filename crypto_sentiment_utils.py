#!/usr/bin/env python3
"""
🛠️ Crypto Sentiment Analysis Utilities
Helper functions and utilities for crypto sentiment analysis

This module provides:
- Formatting and display utilities
- Data export functions
- Quick analysis functions
- Batch processing utilities
"""

import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from crypto_sentiment_analyzer import CryptoSentimentAnalyzer

def format_sentiment_report(results: Dict) -> str:
    """
    Format sentiment analysis results into a readable report.
    
    Args:
        results: Results dictionary from CryptoSentimentAnalyzer
        
    Returns:
        Formatted string report
    """
    if not results.get('success'):
        return f"❌ Analysis failed: {results.get('error', 'Unknown error')}"
    
    coin_name = results['coin_name']
    overall_sentiment = results['overall_sentiment']
    sentiment_strength = results['sentiment_strength']
    vader_avg = results['sentiment_scores']['vader_average']
    textblob_avg = results['sentiment_scores']['textblob_average']
    
    # Determine emoji
    if overall_sentiment == 'Bullish':
        emoji = "🟢" if sentiment_strength == "Strong" else "🟡"
    elif overall_sentiment == 'Bearish':
        emoji = "🔴" if sentiment_strength == "Strong" else "🟠"
    else:
        emoji = "⚪"
    
    report = f"""
🪙 **{coin_name} Sentiment Analysis Report**
{'=' * 60}

{emoji} **Overall Sentiment**: {sentiment_strength} {overall_sentiment}

📊 **Sentiment Scores**:
   • VADER Average: {vader_avg:.3f}
   • TextBlob Average: {textblob_avg:.3f}

📰 **Data Summary**:
   • Articles Analyzed: {results['data_summary']['relevant_articles']}
   • Sources Used: {results['data_summary']['sources_used']}
   • Total Articles Collected: {results['data_summary']['total_articles_collected']}

📈 **VADER Distribution**:
   • Positive: {results['sentiment_scores']['vader_distribution']['Positive']}
   • Negative: {results['sentiment_scores']['vader_distribution']['Negative']}
   • Neutral: {results['sentiment_scores']['vader_distribution']['Neutral']}

📊 **TextBlob Distribution**:
   • Positive: {results['sentiment_scores']['textblob_distribution']['Positive']}
   • Negative: {results['sentiment_scores']['textblob_distribution']['Negative']}
   • Neutral: {results['sentiment_scores']['textblob_distribution']['Neutral']}
"""

    # Add most positive/negative articles
    if results.get('most_positive_article'):
        most_pos = results['most_positive_article']
        report += f"""
📈 **Most Positive Article**:
   Title: {most_pos['article']['title'][:80]}...
   Score: {most_pos['vader']['compound']:.3f}
   Source: {most_pos['article']['source']}
"""

    if results.get('most_negative_article'):
        most_neg = results['most_negative_article']
        report += f"""
📉 **Most Negative Article**:
   Title: {most_neg['article']['title'][:80]}...
   Score: {most_neg['vader']['compound']:.3f}
   Source: {most_neg['article']['source']}
"""

    # Add AI analysis if available
    if results.get('ai_analysis') and results['ai_analysis'].get('success'):
        report += f"""
🤖 **AI Analysis**:
{results['ai_analysis']['analysis']}
"""

    report += f"""
📅 **Analysis Timestamp**: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
"""

    return report

def export_to_json(results: Dict, filename: Optional[str] = None) -> str:
    """
    Export sentiment analysis results to JSON file.
    
    Args:
        results: Results dictionary from CryptoSentimentAnalyzer
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Path to the exported file
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        coin_name = results.get('coin_name', 'unknown').lower()
        filename = f"sentiment_analysis_{coin_name}_{timestamp}.json"
    
    # Convert datetime objects to strings for JSON serialization
    export_data = json.loads(json.dumps(results, default=str))
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return filename

def export_to_csv(results: Dict, filename: Optional[str] = None) -> str:
    """
    Export sentiment analysis results to CSV file.
    
    Args:
        results: Results dictionary from CryptoSentimentAnalyzer
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Path to the exported file
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        coin_name = results.get('coin_name', 'unknown').lower()
        filename = f"sentiment_analysis_{coin_name}_{timestamp}.csv"
    
    if not results.get('success') or not results.get('articles'):
        return filename
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Title', 'Source', 'URL', 'VADER_Sentiment', 'VADER_Score',
            'TextBlob_Sentiment', 'TextBlob_Score', 'Method', 'Timestamp'
        ])
        
        # Write article data
        for sentiment_data in results['articles']:
            article = sentiment_data['article']
            vader = sentiment_data['vader']
            textblob = sentiment_data['textblob']
            
            writer.writerow([
                article.get('title', ''),
                article.get('source', ''),
                article.get('url', ''),
                vader['sentiment'],
                vader['compound'],
                textblob['sentiment'],
                textblob['polarity'],
                article.get('method', ''),
                article.get('timestamp', '')
            ])
    
    return filename

def quick_sentiment_check(coin_name: str) -> str:
    """
    Quick sentiment check for a cryptocurrency.

    Args:
        coin_name: Name of the cryptocurrency

    Returns:
        Quick sentiment summary string
    """
    try:
        analyzer = CryptoSentimentAnalyzer()

        # Try fast analysis first
        results = analyzer.analyze_crypto_sentiment(coin_name, include_ai=False, verbose=False, fast_mode=True)

        if results.get('success'):
            return f"{results['sentiment_strength']} {results['overall_sentiment']}"
        else:
            return "Sentiment analysis unavailable"

    except Exception as e:
        return f"Sentiment unavailable: {str(e)[:30]}..."

def get_trading_signal(coin_name: str) -> Dict:
    """
    Get trading signal for a cryptocurrency.
    
    Args:
        coin_name: Name of the cryptocurrency
        
    Returns:
        Trading signal dictionary
    """
    analyzer = CryptoSentimentAnalyzer()
    return analyzer.get_trading_signal(coin_name)

def batch_analyze_cryptos(coin_names: List[str], include_ai: bool = False) -> Dict[str, Dict]:
    """
    Analyze sentiment for multiple cryptocurrencies.
    
    Args:
        coin_names: List of cryptocurrency names
        include_ai: Whether to include AI analysis
        
    Returns:
        Dictionary mapping coin names to analysis results
    """
    analyzer = CryptoSentimentAnalyzer()
    results = {}
    
    for coin_name in coin_names:
        print(f"🔍 Analyzing {coin_name}...")
        try:
            result = analyzer.analyze_crypto_sentiment(coin_name, include_ai=include_ai, verbose=False)
            results[coin_name] = result
        except Exception as e:
            results[coin_name] = {
                'coin_name': coin_name,
                'error': str(e),
                'success': False
            }
    
    return results

def compare_crypto_sentiments(coin_names: List[str]) -> str:
    """
    Compare sentiment across multiple cryptocurrencies.
    
    Args:
        coin_names: List of cryptocurrency names
        
    Returns:
        Formatted comparison report
    """
    results = batch_analyze_cryptos(coin_names, include_ai=False)
    
    report = "🔍 **Crypto Sentiment Comparison**\n"
    report += "=" * 50 + "\n\n"
    
    successful_results = {k: v for k, v in results.items() if v.get('success')}
    
    if not successful_results:
        return report + "❌ No successful analyses to compare.\n"
    
    # Sort by sentiment strength
    sorted_cryptos = sorted(
        successful_results.items(),
        key=lambda x: x[1]['sentiment_scores']['vader_average'],
        reverse=True
    )
    
    for coin_name, result in sorted_cryptos:
        sentiment = result['overall_sentiment']
        strength = result['sentiment_strength']
        vader_avg = result['sentiment_scores']['vader_average']
        
        if sentiment == 'Bullish':
            emoji = "🟢" if strength == "Strong" else "🟡"
        elif sentiment == 'Bearish':
            emoji = "🔴" if strength == "Strong" else "🟠"
        else:
            emoji = "⚪"
        
        report += f"{emoji} **{coin_name}**: {strength} {sentiment} ({vader_avg:.3f})\n"
        report += f"   Articles: {result['data_summary']['relevant_articles']} | "
        report += f"Sources: {result['data_summary']['sources_used']}\n\n"
    
    return report

def create_sentiment_dashboard(coin_names: List[str]) -> str:
    """
    Create a sentiment dashboard for multiple cryptocurrencies.
    
    Args:
        coin_names: List of cryptocurrency names
        
    Returns:
        Formatted dashboard string
    """
    results = batch_analyze_cryptos(coin_names, include_ai=False)
    
    dashboard = f"""
🚀 **Crypto Sentiment Dashboard**
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}

"""
    
    successful_results = {k: v for k, v in results.items() if v.get('success')}
    failed_results = {k: v for k, v in results.items() if not v.get('success')}
    
    if successful_results:
        dashboard += "📊 **Sentiment Overview**:\n\n"
        
        for coin_name, result in successful_results.items():
            sentiment = result['overall_sentiment']
            strength = result['sentiment_strength']
            vader_avg = result['sentiment_scores']['vader_average']
            textblob_avg = result['sentiment_scores']['textblob_average']
            
            if sentiment == 'Bullish':
                emoji = "🟢" if strength == "Strong" else "🟡"
            elif sentiment == 'Bearish':
                emoji = "🔴" if strength == "Strong" else "🟠"
            else:
                emoji = "⚪"
            
            dashboard += f"{emoji} **{coin_name}**\n"
            dashboard += f"   Sentiment: {strength} {sentiment}\n"
            dashboard += f"   VADER: {vader_avg:.3f} | TextBlob: {textblob_avg:.3f}\n"
            dashboard += f"   Data: {result['data_summary']['relevant_articles']} articles from {result['data_summary']['sources_used']} sources\n\n"
    
    if failed_results:
        dashboard += "❌ **Failed Analyses**:\n\n"
        for coin_name, result in failed_results.items():
            dashboard += f"   • {coin_name}: {result.get('error', 'Unknown error')}\n"
    
    dashboard += f"\n📈 **Summary**: {len(successful_results)} successful, {len(failed_results)} failed\n"
    
    return dashboard

# Example usage functions
def demo_single_analysis():
    """Demonstrate single cryptocurrency analysis."""
    print("🤖 Demo: Single Cryptocurrency Analysis")
    print("=" * 50)
    
    analyzer = CryptoSentimentAnalyzer()
    results = analyzer.analyze_crypto_sentiment("Bitcoin", include_ai=True, verbose=True)
    
    print("\n" + format_sentiment_report(results))

def demo_batch_analysis():
    """Demonstrate batch cryptocurrency analysis."""
    print("🤖 Demo: Batch Cryptocurrency Analysis")
    print("=" * 50)
    
    cryptos = ["Bitcoin", "Ethereum", "Solana"]
    dashboard = create_sentiment_dashboard(cryptos)
    print(dashboard)

def demo_trading_signals():
    """Demonstrate trading signal generation."""
    print("🤖 Demo: Trading Signal Generation")
    print("=" * 50)
    
    cryptos = ["Bitcoin", "Ethereum", "Cardano"]
    
    for crypto in cryptos:
        signal = get_trading_signal(crypto)
        print(f"💰 {crypto}: {signal['signal']} (Confidence: {signal['confidence']}%)")
        print(f"   Reason: {signal['reason']}\n")

if __name__ == "__main__":
    # Run demos
    demo_single_analysis()
    print("\n" + "="*60 + "\n")
    demo_batch_analysis()
    print("\n" + "="*60 + "\n")
    demo_trading_signals()
