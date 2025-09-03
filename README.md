# 🚀 Crypto Trading Platform with AI Analysis

A comprehensive cryptocurrency trading platform that combines **OpenRouter (DeepSeek) AI** with **Binance API** for intelligent crypto analysis, technical indicators, and sentiment analysis.

## 🌟 Features

### 🤖 AI-Powered Analysis
- **OpenRouter Integration**: Uses DeepSeek AI for intelligent crypto analysis
- **Ticker Extraction**: Automatically extracts crypto symbols from natural language
- **Market Analysis**: AI-powered insights and recommendations
- **Sentiment Analysis**: News and social media sentiment tracking

### 📊 Professional Technical Analysis
- **Industry-Standard Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Multi-Timeframe Analysis**: Daily, 4H, 1H perspectives
- **Volume Analysis**: OBV, Volume trends, and patterns
- **Volatility Indicators**: ATR, Bollinger Band width
- **Support/Resistance**: Automated level detection

### 📈 Real-Time Data
- **Binance API Integration**: Live price feeds and historical data
- **Yahoo Finance Fallback**: Reliable data source backup
- **Data Validation**: Ensures data quality and integrity
- **Multiple Cryptocurrencies**: BTC, ETH, ADA, SOL, and more

### 🖥️ User Interfaces
- **Gradio Web App**: Interactive web interface for easy use
- **Jupyter Notebooks**: Professional analysis and visualization
- **Command Line Tools**: For automated analysis and scripting

### 🔍 Sentiment Analysis
- **Web Scraping**: News and social media sentiment
- **Real-time Updates**: Latest market sentiment tracking
- **Sentiment Scoring**: Quantified market mood analysis

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/crypto-trading-platform.git
cd crypto-trading-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API keys**
```bash
cp .env.template .env
# Edit .env file with your API keys
```

4. **Run the application**
```bash
# Web interface
python crypto_gradio_app.py

# Technical analysis
python crypto_ta_simple.py

# Jupyter notebooks
jupyter notebook
```

## 🔑 API Configuration

### Required API Keys

1. **OpenRouter API Key** (for AI analysis)
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Add to `.env`: `OPENROUTER_API_KEY=your_key_here`

2. **Binance API Keys** (optional, for enhanced data)
   - Create at [Binance API](https://www.binance.com/en/my/settings/api-management)
   - Add to `.env`: `BINANCE_API_KEY=your_key` and `BINANCE_SECRET_KEY=your_secret`

### Environment Variables
```env
OPENROUTER_API_KEY=your_openrouter_api_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
```

## 🚀 Usage

### Web Interface
```bash
python crypto_gradio_app.py
```
Open http://localhost:7860 in your browser

### Technical Analysis Script
```python
# Modify configuration in crypto_ta_simple.py
SYMBOL = 'BTC'      # Change to any crypto
PERIOD = '3mo'      # Analysis period
INTERVAL = '1d'     # Data interval

python crypto_ta_simple.py
```

### Jupyter Notebooks
- `crypto_trading_platform.ipynb` - Main analysis notebook
- `crypto_technical_analysis.ipynb` - Technical analysis focus
- `test_crypto_ta.ipynb` - Testing and validation
- `crypto_sentiment_notebook.ipynb` - Sentiment analysis

## 📊 Key Components

### Core Modules
- `openrouter_config.py` - AI analysis configuration
- `binance_api.py` - Cryptocurrency data fetching
- `crypto_ta_simple.py` - Technical analysis engine
- `crypto_sentiment_analyzer.py` - Sentiment analysis
- `crypto_gradio_app.py` - Web interface

### Analysis Features
- **Price Action**: Candlestick patterns, trends
- **Technical Indicators**: 20+ professional indicators
- **Volume Analysis**: Trading volume patterns
- **Market Sentiment**: News and social sentiment
- **Risk Assessment**: Volatility and risk metrics

## 🎯 Example Analysis Output

```
🚀 Starting Technical Analysis for BTC
📊 Period: 3mo, Interval: 1d
============================================================

✅ Successfully loaded 90 records
📅 Date range: 2024-06-01 to 2024-09-01
💰 Current price: $43,250.67

📊 Technical Analysis Summary:
==================================================
💰 Current Price: $43,250.67
📈 Price vs SMA(20): 🟢 Above (+2.3%)
📈 Price vs SMA(50): 🟢 Above (+5.7%)
⚡ RSI: 52.3 (🟡 Neutral)
📊 MACD: 🟢 Bullish
🎯 Bollinger Bands: 🟡 Within Bands (Normal)
📊 Volatility (ATR): 🟡 MEDIUM (3.2%)
📦 Volume Trend: 🟢 Above Average (1.4x avg)

🎯 Overall Technical Assessment:
===================================
📊 Market Sentiment: 🟢 BULLISH
📈 Bullish Signals: 4
📉 Bearish Signals: 1
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
jupyter notebook test_crypto_ta.ipynb
```

The test notebook validates:
- ✅ Data fetching from multiple sources
- ✅ Technical indicator calculations
- ✅ Chart generation and visualization
- ✅ Error handling and fallbacks
- ✅ Multi-cryptocurrency support

## 📁 Project Structure

```
crypto-trading-platform/
├── 📄 README.md                          # This file
├── 📄 requirements.txt                   # Python dependencies
├── 📄 .env.template                      # Environment variables template
├── 🔧 crypto_gradio_app.py              # Web interface
├── 🔧 crypto_ta_simple.py               # Technical analysis engine
├── 🔧 openrouter_config.py              # AI configuration
├── 🔧 binance_api.py                     # Data fetching
├── 📊 crypto_trading_platform.ipynb     # Main analysis notebook
├── 📊 crypto_technical_analysis.ipynb   # Technical analysis notebook
├── 📊 test_crypto_ta.ipynb              # Testing notebook
├── 📊 crypto_sentiment_notebook.ipynb   # Sentiment analysis
└── 📁 crypto_trading_platform/          # Additional notebooks
    └── 📁 data/
        ├── crypto_analysis.ipynb
        └── web_scraping.ipynb
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. It is not financial advice. Always do your own research and consider the risks before making any trading decisions.

## 🙏 Acknowledgments

- **OpenRouter** for AI analysis capabilities
- **Binance** for cryptocurrency data
- **Technical Analysis Library (ta)** for indicators
- **Gradio** for the web interface
- **Yahoo Finance** for backup data

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/crypto-trading-platform/issues) page
2. Create a new issue with detailed information
3. Include error messages and system information

---

**Made with ❤️ for the crypto community**
