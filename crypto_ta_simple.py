# 📊 Cryptocurrency Technical Analysis
# Professional-Grade Technical Analysis Following Industry Standards

import sys
import os
import warnings
from datetime import datetime, timedelta
import math

warnings.filterwarnings('ignore')

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🔧 Installing required packages...")

# Install required packages
required_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'ta', 'yfinance']

for package in required_packages:
    try:
        __import__(package)
        print(f"✅ {package} already installed")
    except ImportError:
        print(f"📦 Installing {package}...")
        os.system(f"pip install {package}")

# Import all required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import yfinance as yf

# Technical Analysis library
import ta
from ta.trend import MACD, EMAIndicator, SMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

# Try to import custom modules
try:
    from binance_api import binance_api
    print("✅ Custom Binance API module imported")
    USE_BINANCE = True
except ImportError:
    print("⚠️ Custom Binance API not available, will use yfinance as fallback")
    USE_BINANCE = False

# Configure plotting
plt.style.use('default')
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10

# Configure pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.precision', 4)

print("\n🎉 All dependencies loaded successfully!")
print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# CONFIGURATION SECTION - MODIFY THESE VALUES
# =============================================================================

SYMBOL = 'BTC'      # Options: 'BTC', 'ETH', 'ADA', 'SOL', 'MATIC', etc.
PERIOD = '3mo'      # Options: '1mo', '3mo', '6mo', '1y', '2y'
INTERVAL = '1d'     # Options: '1d', '1h', '4h'

print(f"\n🚀 Configuration Set:")
print(f"   Symbol: {SYMBOL}")
print(f"   Period: {PERIOD}")
print(f"   Interval: {INTERVAL}")

# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

def get_crypto_data(symbol, period='3mo', interval='1d'):
    """
    Fetch cryptocurrency data from multiple sources with fallback.
    """
    
    # Try Binance API first if available
    if USE_BINANCE and interval == '1d':
        try:
            print(f"📊 Fetching {symbol} data from Binance API...")
            
            # Convert period to days
            period_days = {
                '1mo': 30, '3mo': 90, '6mo': 180, 
                '1y': 365, '2y': 730
            }.get(period, 90)
            
            result = binance_api.get_historical_data(symbol, interval='1d', days=period_days)
            
            if result.get('success'):
                data_list = result['data']
                df = pd.DataFrame(data_list)
                
                # Rename columns to standard format
                df = df.rename(columns={
                    'open': 'Open', 'high': 'High', 'low': 'Low', 
                    'close': 'Close', 'volume': 'Volume'
                })
                
                df.set_index('timestamp', inplace=True)
                df.index = pd.to_datetime(df.index)
                
                print(f"✅ Successfully fetched {len(df)} records from Binance")
                return df
                
        except Exception as e:
            print(f"⚠️ Binance API failed: {e}")
    
    # Fallback to yfinance
    try:
        print(f"📊 Fetching {symbol} data from Yahoo Finance...")
        
        # Convert symbol to Yahoo Finance format
        yf_symbol = f"{symbol}-USD"
        
        # Fetch data
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data found for {yf_symbol}")
        
        # Ensure we have the required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        print(f"✅ Successfully fetched {len(df)} records from Yahoo Finance")
        return df[required_cols]
        
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return None

def validate_data(df):
    """Validate and clean the data."""
    if df is None or df.empty:
        return None
    
    # Remove any rows with NaN values
    df = df.dropna()
    
    # Ensure positive values
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df[df[col] > 0]
    
    # Validate OHLC relationships
    df = df[(df['High'] >= df['Low']) & 
            (df['High'] >= df['Open']) & 
            (df['High'] >= df['Close']) &
            (df['Low'] <= df['Open']) & 
            (df['Low'] <= df['Close'])]
    
    return df.sort_index()

# =============================================================================
# TECHNICAL ANALYSIS CLASS
# =============================================================================

class TechnicalAnalyzer:
    """
    Professional Technical Analysis class following industry standards.
    """
    
    def __init__(self, df):
        """Initialize with OHLCV data."""
        self.df = df.copy()
        self.indicators = {}
        
    def add_moving_averages(self):
        """Add various moving averages."""
        # Simple Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            if len(self.df) >= period:
                self.df[f'SMA_{period}'] = SMAIndicator(
                    close=self.df['Close'], window=period
                ).sma_indicator()
        
        # Exponential Moving Averages
        for period in [12, 26, 50, 200]:
            if len(self.df) >= period:
                self.df[f'EMA_{period}'] = EMAIndicator(
                    close=self.df['Close'], window=period
                ).ema_indicator()
        
        print("✅ Moving averages calculated")
    
    def add_trend_indicators(self):
        """Add trend-following indicators."""
        # MACD
        macd = MACD(close=self.df['Close'])
        self.df['MACD'] = macd.macd()
        self.df['MACD_Signal'] = macd.macd_signal()
        self.df['MACD_Histogram'] = macd.macd_diff()
        
        # ADX (Average Directional Index)
        if len(self.df) >= 14:
            adx = ADXIndicator(high=self.df['High'], low=self.df['Low'], close=self.df['Close'])
            self.df['ADX'] = adx.adx()
            self.df['ADX_Pos'] = adx.adx_pos()
            self.df['ADX_Neg'] = adx.adx_neg()
        
        print("✅ Trend indicators calculated")
    
    def add_momentum_indicators(self):
        """Add momentum oscillators."""
        # RSI
        if len(self.df) >= 14:
            rsi = RSIIndicator(close=self.df['Close'])
            self.df['RSI'] = rsi.rsi()
        
        # Stochastic Oscillator
        if len(self.df) >= 14:
            stoch = StochasticOscillator(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['Stoch_K'] = stoch.stoch()
            self.df['Stoch_D'] = stoch.stoch_signal()
        
        # Williams %R
        if len(self.df) >= 14:
            williams = WilliamsRIndicator(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['Williams_R'] = williams.williams_r()
        
        print("✅ Momentum indicators calculated")
    
    def add_volatility_indicators(self):
        """Add volatility indicators."""
        # Bollinger Bands
        if len(self.df) >= 20:
            bb = BollingerBands(close=self.df['Close'])
            self.df['BB_Upper'] = bb.bollinger_hband()
            self.df['BB_Middle'] = bb.bollinger_mavg()
            self.df['BB_Lower'] = bb.bollinger_lband()
            self.df['BB_Width'] = (self.df['BB_Upper'] - self.df['BB_Lower']) / self.df['BB_Middle']
        
        # Average True Range
        if len(self.df) >= 14:
            atr = AverageTrueRange(
                high=self.df['High'], low=self.df['Low'], close=self.df['Close']
            )
            self.df['ATR'] = atr.average_true_range()
        
        print("✅ Volatility indicators calculated")
    
    def add_volume_indicators(self):
        """Add volume-based indicators."""
        # On Balance Volume
        obv = OnBalanceVolumeIndicator(
            close=self.df['Close'], volume=self.df['Volume']
        )
        self.df['OBV'] = obv.on_balance_volume()

        # Volume Simple Moving Average (manual calculation)
        if len(self.df) >= 20:
            self.df['Volume_SMA'] = self.df['Volume'].rolling(window=20).mean()

        print("✅ Volume indicators calculated")
    
    def calculate_all_indicators(self):
        """Calculate all technical indicators."""
        print("🔄 Calculating technical indicators...")
        
        self.add_moving_averages()
        self.add_trend_indicators()
        self.add_momentum_indicators()
        self.add_volatility_indicators()
        self.add_volume_indicators()
        
        print("✅ All technical indicators calculated successfully!")
        return self.df

print("✅ TechnicalAnalyzer class defined successfully!")

# =============================================================================
# MAIN ANALYSIS EXECUTION
# =============================================================================

print(f"\n🚀 Starting Technical Analysis for {SYMBOL}")
print(f"📊 Period: {PERIOD}, Interval: {INTERVAL}")
print("=" * 60)

# Step 1: Fetch and validate data
print("\n1️⃣ Fetching market data...")
raw_data = get_crypto_data(SYMBOL, period=PERIOD, interval=INTERVAL)

if raw_data is None or raw_data.empty:
    print("❌ Failed to fetch data. Please check your internet connection and try again.")
    sys.exit(1)

# Validate data
data = validate_data(raw_data)

if data is None or data.empty:
    print("❌ Data validation failed.")
    sys.exit(1)

print(f"✅ Successfully loaded {len(data)} records")
print(f"📅 Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
print(f"💰 Current price: ${data['Close'].iloc[-1]:,.2f}")

# Step 2: Calculate technical indicators
print("\n2️⃣ Calculating technical indicators...")
analyzer = TechnicalAnalyzer(data)
analyzed_data = analyzer.calculate_all_indicators()

print(f"\n✅ Technical Analysis Complete for {SYMBOL}!")
print(f"📊 Run this script to see comprehensive technical analysis charts and signals.")
print(f"💡 Modify the SYMBOL, PERIOD, and INTERVAL variables at the top to analyze different cryptocurrencies.")
