#!/usr/bin/env python3
"""
🚀 Crypto Trading Platform - Gradio Interface
Enhanced with modular Binance data analysis and crypto sentiment analysis

Features:
- Natural language crypto queries with DeepSeek AI
- Real-time Binance API data integration
- Crypto sentiment analysis with web scraping
- Professional trading insights and recommendations
- Clean, modular architecture
"""

import gradio as gr
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our enhanced modular functions
from binance_data_analyzer import BinanceDataAnalyzer
from crypto_sentiment_analyzer import CryptoSentimentAnalyzer
from crypto_sentiment_utils import quick_sentiment_check, get_trading_signal, format_sentiment_report

# Initialize analyzers
binance_analyzer = BinanceDataAnalyzer()
sentiment_analyzer = CryptoSentimentAnalyzer()

def process_crypto_query(user_query):
    """
    Enhanced crypto query processing with modular functions.
    Complete pipeline: Extract ticker → Fetch price → Get AI analysis → Get sentiment → Format results
    """
    if not user_query.strip():
        return "Please enter a cryptocurrency query!", ""

    try:
        # Step 1: Use Binance analyzer for price data and AI analysis
        binance_result = binance_analyzer.process_crypto_query(user_query, include_historical=False)

        if not binance_result.get('success'):
            return f"❌ {binance_result.get('error', 'Unknown error')}", ""

        # Extract data from Binance result
        ticker = binance_result['ticker']
        price_data = binance_result['price_data']
        ai_analysis = binance_result['ai_analysis']

        # Step 2: Get sentiment analysis for the cryptocurrency (with timeout protection)
        coin_name = ticker.replace('USDT', '').replace('BTC', '').replace('ETH', '')
        if not coin_name:
            coin_name = 'Bitcoin' if 'BTC' in ticker else 'Ethereum' if 'ETH' in ticker else ticker[:3]

        try:
            # Use faster sentiment analysis with limited data collection
            sentiment_result = sentiment_analyzer.analyze_crypto_sentiment(
                coin_name,
                include_ai=False,
                verbose=False
            )

            if sentiment_result.get('success'):
                sentiment = f"{sentiment_result['sentiment_strength']} {sentiment_result['overall_sentiment']}"

                # Generate trading signal based on sentiment
                vader_avg = sentiment_result['sentiment_scores']['vader_average']
                if vader_avg > 0.2:
                    signal = 'BUY'
                    confidence = min(85, int(vader_avg * 100 + 50))
                elif vader_avg < -0.2:
                    signal = 'SELL'
                    confidence = min(85, int(abs(vader_avg) * 100 + 50))
                else:
                    signal = 'HOLD'
                    confidence = 60

                trading_signal = {
                    'signal': signal,
                    'confidence': confidence,
                    'reason': f"Based on {sentiment_result['data_summary']['relevant_articles']} articles"
                }
            else:
                sentiment = "Sentiment analysis unavailable"
                trading_signal = {
                    'signal': 'HOLD',
                    'confidence': 50,
                    'reason': 'Sentiment data unavailable'
                }

        except Exception as e:
            sentiment = "Sentiment analysis unavailable"
            trading_signal = {
                'signal': 'HOLD',
                'confidence': 50,
                'reason': f'Sentiment analysis failed: {str(e)[:50]}...'
            }

        # Step 3: Format comprehensive response
        response = format_comprehensive_response(
            user_query, ticker, price_data, ai_analysis, sentiment, trading_signal
        )

        # Step 4: Create detailed analysis for second output
        detailed_analysis = create_detailed_analysis(binance_result, sentiment, trading_signal)

        return response, detailed_analysis

    except Exception as e:
        error_msg = f"❌ Query processing failed: {str(e)}"
        return error_msg, ""

def format_comprehensive_response(user_query, ticker, price_data, ai_analysis, sentiment, trading_signal):
    """Format the main response with all key information."""

    # Determine signal emoji
    signal_emoji = "🟢" if trading_signal['signal'] == 'BUY' else "🔴" if trading_signal['signal'] == 'SELL' else "🟡"

    response = f"""
🎯 **Enhanced Crypto Analysis Results**

**Query:** {user_query}
**Cryptocurrency:** {ticker}

💰 **Current Market Data:**
• **Price:** ${price_data['current_price']:,.2f}
• **24h Change:** {price_data['price_change_24h']:+.2f}%
• **24h Range:** ${price_data['low_24h']:,.2f} - ${price_data['high_24h']:,.2f}
• **24h Volume:** {price_data['volume_24h']:,.0f}

🤖 **AI Market Analysis:**
{ai_analysis.get('analysis', 'Analysis not available') if ai_analysis.get('success') else f"Analysis failed: {ai_analysis.get('error', 'Unknown error')}"}

📊 **Sentiment & Trading Signal:**
• **Market Sentiment:** {sentiment}
• **Trading Signal:** {signal_emoji} {trading_signal['signal']} (Confidence: {trading_signal['confidence']}%)
• **Recommendation:** {trading_signal['reason']}

⏰ **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """

    return response.strip()

def create_detailed_analysis(binance_result, sentiment, trading_signal):
    """Create detailed technical analysis."""

    ticker = binance_result['ticker']
    price_data = binance_result['price_data']

    # Calculate some basic metrics
    price_change_abs = price_data['current_price'] * (price_data['price_change_24h'] / 100)
    high_low_range = price_data['high_24h'] - price_data['low_24h']
    current_position = ((price_data['current_price'] - price_data['low_24h']) / high_low_range) * 100 if high_low_range > 0 else 50

    detailed = f"""
📈 **Detailed Technical Analysis for {ticker}**

**Price Metrics:**
• Absolute 24h Change: ${price_change_abs:+,.2f}
• Current Position in 24h Range: {current_position:.1f}%
• Price Volatility (High-Low): ${high_low_range:,.2f} ({(high_low_range/price_data['current_price']*100):.2f}%)

**Market Assessment:**
• Trend Direction: {'Bullish' if price_data['price_change_24h'] > 0 else 'Bearish' if price_data['price_change_24h'] < 0 else 'Sideways'}
• Volume Analysis: {'High' if price_data['volume_24h'] > 1000000 else 'Moderate' if price_data['volume_24h'] > 100000 else 'Low'} trading activity
• Support Level: ${price_data['low_24h']:,.2f}
• Resistance Level: ${price_data['high_24h']:,.2f}

**Sentiment Analysis:**
• News Sentiment: {sentiment}
• Signal Strength: {trading_signal['confidence']}% confidence
• Risk Level: {'High' if trading_signal['confidence'] < 60 else 'Medium' if trading_signal['confidence'] < 80 else 'Low'}

**Data Sources:**
• Price Data: Binance API (Real-time)
• AI Analysis: DeepSeek via OpenRouter
• Sentiment: Multi-source news analysis (VADER, TextBlob, AI)
    """

    return detailed.strip()

def get_quick_price(crypto_input):
    """Quick price lookup function."""
    if not crypto_input.strip():
        return "Please enter a cryptocurrency name or symbol."

    try:
        quick_price = binance_analyzer.get_quick_price(crypto_input)
        return f"💰 {quick_price}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def analyze_crypto_sentiment(crypto_name):
    """Dedicated sentiment analysis function."""
    if not crypto_name.strip():
        return "Please enter a cryptocurrency name."

    try:
        # Get comprehensive sentiment analysis
        results = sentiment_analyzer.analyze_crypto_sentiment(crypto_name, include_ai=True, verbose=False)

        if results.get('success'):
            # Format the sentiment report
            report = format_sentiment_report(results)
            return report
        else:
            return f"❌ Sentiment analysis failed: {results.get('error', 'Unknown error')}"

    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_market_overview():
    """Get overview of major cryptocurrencies."""
    major_cryptos = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
    overview = "🌍 **Major Cryptocurrency Overview**\n\n"

    for ticker in major_cryptos:
        try:
            price_data = binance_analyzer.get_current_price_data(ticker)
            if price_data.get('success'):
                coin_name = ticker.replace('USDT', '')
                change_emoji = "🟢" if price_data['price_change_24h'] > 0 else "🔴" if price_data['price_change_24h'] < 0 else "🟡"
                overview += f"{change_emoji} **{coin_name}**: ${price_data['current_price']:,.2f} ({price_data['price_change_24h']:+.2f}%)\n"
        except:
            continue

    overview += f"\n⏰ Updated: {datetime.now().strftime('%H:%M:%S')}"
    return overview

def test_system_status():
    """Test system connections and status."""
    results = []

    # Test Binance analyzer
    try:
        test_result = binance_analyzer.get_current_price_data("BTCUSDT")
        if test_result.get('success'):
            results.append("✅ Binance Data Analyzer: Working")
        else:
            results.append("❌ Binance Data Analyzer: Failed")
    except Exception as e:
        results.append(f"❌ Binance Data Analyzer: Error - {str(e)}")

    # Test sentiment analyzer
    try:
        test_sentiment = sentiment_analyzer.get_quick_sentiment("Bitcoin")
        results.append("✅ Sentiment Analyzer: Working")
    except Exception as e:
        results.append(f"❌ Sentiment Analyzer: Error - {str(e)}")

    # Check API keys
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')

    results.append(f"🔑 OpenRouter API: {'✅ Configured' if openrouter_key else '❌ Missing'}")
    results.append(f"🔑 Tavily API: {'✅ Configured' if tavily_key else '❌ Missing'}")

    return "\n".join(results)

# Create the enhanced Gradio interface
with gr.Blocks(title="🚀 Enhanced Crypto Trading Platform", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🚀 Enhanced Crypto Trading Platform
    ## AI-Powered Cryptocurrency Analysis with Sentiment Intelligence

    **Enhanced Features:**
    - 🤖 Natural language query processing with DeepSeek AI
    - 📊 Real-time price data from Binance API
    - 📰 Multi-source crypto sentiment analysis
    - 💰 AI-powered trading signals and recommendations
    - 🎯 Comprehensive market intelligence
    """)
    
    with gr.Tabs():
        # Tab 1: Enhanced AI Query with Sentiment
        with gr.Tab("🤖 AI Query + Sentiment"):
            gr.Markdown("### Ask about any cryptocurrency with AI analysis and sentiment intelligence!")

            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="Enter your crypto query",
                        placeholder="e.g., 'What's the current price of Bitcoin?' or 'How is Ethereum performing?'",
                        lines=2
                    )
                    query_btn = gr.Button("🔍 Analyze with AI + Sentiment", variant="primary")

                with gr.Column(scale=1):
                    gr.Markdown("""
                    **Example queries:**
                    - What's Bitcoin doing today?
                    - Show me Ethereum price
                    - How is Solana performing?
                    - Tell me about Cardano
                    - Analyze Polygon's market
                    """)

            with gr.Row():
                with gr.Column():
                    analysis_output = gr.Textbox(
                        label="📊 Comprehensive Analysis",
                        lines=20,
                        max_lines=25
                    )

                with gr.Column():
                    detailed_analysis = gr.Textbox(
                        label="📈 Detailed Technical Analysis",
                        lines=20,
                        max_lines=25
                    )

        # Tab 2: Quick Price Lookup
        with gr.Tab("💰 Quick Price"):
            gr.Markdown("### Get quick price information for any cryptocurrency")

            with gr.Row():
                price_input = gr.Textbox(
                    label="Cryptocurrency",
                    placeholder="e.g., Bitcoin, BTC, BTCUSDT",
                    lines=1
                )
                price_btn = gr.Button("💰 Get Price", variant="secondary")

            price_output = gr.Textbox(
                label="Price Information",
                lines=3
            )

        # Tab 3: Sentiment Analysis
        with gr.Tab("📊 Sentiment Analysis"):
            gr.Markdown("### Deep sentiment analysis from crypto news sources")

            with gr.Row():
                sentiment_input = gr.Textbox(
                    label="Cryptocurrency Name",
                    placeholder="e.g., Bitcoin, Ethereum, Solana",
                    lines=1
                )
                sentiment_btn = gr.Button("📊 Analyze Sentiment", variant="secondary")

            sentiment_output = gr.Textbox(
                label="Sentiment Analysis Results",
                lines=15,
                max_lines=20
            )

        # Tab 4: Market Overview
        with gr.Tab("🌍 Market Overview"):
            gr.Markdown("### Overview of major cryptocurrencies")

            overview_btn = gr.Button("🌍 Get Market Overview", variant="secondary")
            overview_output = gr.Textbox(
                label="Market Overview",
                lines=10
            )

        # Tab 5: System Status
        with gr.Tab("🔧 System Status"):
            gr.Markdown("### Check system connections and API status")

            status_btn = gr.Button("🧪 Test System Status", variant="secondary")
            status_output = gr.Textbox(label="System Status", lines=10)

            gr.Markdown("""
            ### Enhanced Setup Instructions:
            1. Create a `.env` file in your project directory
            2. Add your OpenRouter API key: `OPENROUTER_API_KEY=your_key_here`
            3. Add your Tavily API key: `TAVILY_API_KEY=your_key_here`
            4. Run this app and start querying!

            ### Enhanced Features:
            - **AI Analysis:** DeepSeek Chat v3.1 (via OpenRouter)
            - **Price Data:** Binance Public API
            - **Sentiment Analysis:** Multi-source news scraping + AI
            - **Trading Signals:** AI-powered recommendations
            - **Interface:** Gradio with modular functions
            """)

    # Event handlers for all tabs
    query_btn.click(
        fn=process_crypto_query,
        inputs=[query_input],
        outputs=[analysis_output, detailed_analysis]
    )

    price_btn.click(
        fn=get_quick_price,
        inputs=[price_input],
        outputs=[price_output]
    )

    sentiment_btn.click(
        fn=analyze_crypto_sentiment,
        inputs=[sentiment_input],
        outputs=[sentiment_output]
    )

    overview_btn.click(
        fn=get_market_overview,
        outputs=[overview_output]
    )

    status_btn.click(
        fn=test_system_status,
        outputs=[status_output]
    )

if __name__ == "__main__":
    print("🚀 Starting Enhanced Crypto Trading Platform...")
    print("📊 Binance API + DeepSeek AI + Sentiment Analysis Integration")
    print("🌐 Access the interface at: http://localhost:7860")
    print("✨ Features: AI Query, Price Lookup, Sentiment Analysis, Market Overview")
    print("📝 Make sure you have OPENROUTER_API_KEY and TAVILY_API_KEY in your .env file")

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
