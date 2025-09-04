#!/usr/bin/env python3
"""
🚀 Crypto Trading Engine
Complete trading system with portfolio management and trade execution
Integrates with Alibaba Crypto Chatbot for natural language trading
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class Portfolio:
    """Manages user portfolio with holdings and transaction history"""
    
    def __init__(self, user_id: str, initial_balance: float = 10000.0):
        self.user_id = user_id
        self.holdings = {}  # {symbol: amount}
        self.cash_balance = initial_balance
        self.transaction_history = []
        self.created_at = datetime.now().isoformat()
    
    def get_balance(self) -> float:
        """Get current cash balance"""
        return self.cash_balance
    
    def get_holdings(self) -> Dict[str, float]:
        """Get current crypto holdings"""
        return self.holdings.copy()
    
    def get_holding(self, symbol: str) -> float:
        """Get holding amount for specific symbol"""
        return self.holdings.get(symbol.upper(), 0.0)
    
    def add_transaction(self, transaction: Dict):
        """Add transaction to history"""
        transaction['timestamp'] = datetime.now().isoformat()
        transaction['id'] = str(uuid.uuid4())
        self.transaction_history.append(transaction)
    
    def execute_buy(self, symbol: str, amount: float, price: float) -> Dict:
        """Execute buy order"""
        symbol = symbol.upper()
        total_cost = amount * price
        
        if total_cost > self.cash_balance:
            return {
                'success': False,
                'error': f'Insufficient balance. Need ${total_cost:.2f}, have ${self.cash_balance:.2f}'
            }
        
        # Execute trade
        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0.0) + amount
        
        # Record transaction
        transaction = {
            'type': 'BUY',
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'total': total_cost,
            'balance_after': self.cash_balance
        }
        self.add_transaction(transaction)
        
        return {
            'success': True,
            'transaction': transaction,
            'new_balance': self.cash_balance,
            'new_holding': self.holdings[symbol]
        }
    
    def execute_sell(self, symbol: str, amount: float, price: float) -> Dict:
        """Execute sell order"""
        symbol = symbol.upper()
        current_holding = self.holdings.get(symbol, 0.0)
        
        if amount > current_holding:
            return {
                'success': False,
                'error': f'Insufficient {symbol}. Trying to sell {amount}, have {current_holding}'
            }
        
        # Execute trade
        total_value = amount * price
        self.cash_balance += total_value
        self.holdings[symbol] = current_holding - amount
        
        # Remove holding if zero
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        # Record transaction
        transaction = {
            'type': 'SELL',
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'total': total_value,
            'balance_after': self.cash_balance
        }
        self.add_transaction(transaction)
        
        return {
            'success': True,
            'transaction': transaction,
            'new_balance': self.cash_balance,
            'new_holding': self.holdings.get(symbol, 0.0)
        }
    
    def get_portfolio_value(self, price_data: Dict[str, float]) -> Dict:
        """Calculate total portfolio value"""
        crypto_value = 0.0
        holdings_value = {}
        
        for symbol, amount in self.holdings.items():
            price = price_data.get(symbol, 0.0)
            value = amount * price
            crypto_value += value
            holdings_value[symbol] = {
                'amount': amount,
                'price': price,
                'value': value
            }
        
        total_value = self.cash_balance + crypto_value
        
        return {
            'cash_balance': self.cash_balance,
            'crypto_value': crypto_value,
            'total_value': total_value,
            'holdings_detail': holdings_value,
            'timestamp': datetime.now().isoformat()
        }
    
    def to_dict(self) -> Dict:
        """Convert portfolio to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'cash_balance': self.cash_balance,
            'holdings': self.holdings,
            'transaction_count': len(self.transaction_history),
            'created_at': self.created_at,
            'last_updated': datetime.now().isoformat()
        }

class TradingEngine:
    """Core trading engine for executing crypto trades"""
    
    def __init__(self, db_path: str = "trading.db"):
        self.db_path = db_path
        self.portfolios = {}  # In-memory cache
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create portfolios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                user_id TEXT PRIMARY KEY,
                cash_balance REAL,
                holdings TEXT,
                transaction_history TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                type TEXT,
                symbol TEXT,
                amount REAL,
                price REAL,
                total REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_or_create_portfolio(self, user_id: str, initial_balance: float = 10000.0) -> Portfolio:
        """Get existing portfolio or create new one"""
        if user_id in self.portfolios:
            return self.portfolios[user_id]
        
        # Try to load from database
        portfolio = self.load_portfolio(user_id)
        if portfolio:
            self.portfolios[user_id] = portfolio
            return portfolio
        
        # Create new portfolio
        portfolio = Portfolio(user_id, initial_balance)
        self.portfolios[user_id] = portfolio
        self.save_portfolio(portfolio)
        return portfolio
    
    def load_portfolio(self, user_id: str) -> Optional[Portfolio]:
        """Load portfolio from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM portfolios WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        portfolio = Portfolio(user_id, row[1])  # cash_balance
        portfolio.holdings = json.loads(row[2]) if row[2] else {}
        portfolio.transaction_history = json.loads(row[3]) if row[3] else []
        portfolio.created_at = row[4]
        
        return portfolio
    
    def save_portfolio(self, portfolio: Portfolio):
        """Save portfolio to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO portfolios 
            (user_id, cash_balance, holdings, transaction_history, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            portfolio.user_id,
            portfolio.cash_balance,
            json.dumps(portfolio.holdings),
            json.dumps(portfolio.transaction_history),
            portfolio.created_at,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def execute_trade(self, user_id: str, trade_type: str, symbol: str, 
                     amount: float, current_price: float) -> Dict:
        """Execute a trade (buy or sell)"""
        try:
            portfolio = self.get_or_create_portfolio(user_id)
            
            if trade_type.upper() == 'BUY':
                result = portfolio.execute_buy(symbol, amount, current_price)
            elif trade_type.upper() == 'SELL':
                result = portfolio.execute_sell(symbol, amount, current_price)
            else:
                return {
                    'success': False,
                    'error': f'Invalid trade type: {trade_type}. Use BUY or SELL'
                }
            
            if result['success']:
                self.save_portfolio(portfolio)
                result['portfolio_summary'] = portfolio.to_dict()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Trade execution error: {str(e)}'
            }

class TradeCommandParser:
    """Parses natural language trading commands"""
    
    @staticmethod
    def parse_trade_command(message: str) -> Optional[Dict]:
        """Parse trading commands from natural language"""
        message = message.lower().strip()

        # Enhanced buy patterns
        buy_patterns = [
            r'buy\s+(\d+\.?\d*)\s+(\w+)',  # "buy 0.1 btc"
            r'purchase\s+(\d+\.?\d*)\s+(\w+)',  # "purchase 0.5 eth"
            r'get\s+(\d+\.?\d*)\s+(\w+)',  # "get 1 sol"
            r'buy\s+(\w+)',  # "buy btc" (default amount)
            r'buy\s+it',  # "buy it" (needs context)
            r'purchase\s+(\w+)',  # "purchase bitcoin"
            r'get\s+(\w+)',  # "get ethereum"
            r'i\s+want\s+to\s+buy\s+(\d+\.?\d*)\s+(\w+)',  # "i want to buy 0.1 btc"
            r'i\s+want\s+to\s+buy\s+(\w+)',  # "i want to buy bitcoin"
        ]

        # Enhanced sell patterns
        sell_patterns = [
            r'sell\s+(\d+\.?\d*)\s+(\w+)',  # "sell 0.1 btc"
            r'sell\s+all\s+(\w+)',  # "sell all btc"
            r'dump\s+(\d+\.?\d*)\s+(\w+)',  # "dump 0.5 eth"
            r'sell\s+(\w+)',  # "sell btc" (default amount)
            r'sell\s+it',  # "sell it" (needs context)
            r'dump\s+(\w+)',  # "dump bitcoin"
            r'i\s+want\s+to\s+sell\s+(\d+\.?\d*)\s+(\w+)',  # "i want to sell 0.1 btc"
            r'i\s+want\s+to\s+sell\s+(\w+)',  # "i want to sell bitcoin"
        ]

        # Check buy patterns
        for pattern in buy_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()

                # Handle "buy it" case
                if 'buy it' in message or 'purchase it' in message:
                    return {
                        'action': 'BUY',
                        'amount': 0.01,  # Default small amount
                        'symbol': 'BTC',  # Default to BTC
                        'needs_confirmation': True,
                        'original_message': message
                    }

                # Handle patterns with amount and symbol
                if len(groups) == 2 and groups[0] and groups[1]:
                    try:
                        amount = float(groups[0])
                        symbol = groups[1].upper()
                        return {
                            'action': 'BUY',
                            'amount': amount,
                            'symbol': symbol
                        }
                    except ValueError:
                        continue

                # Handle patterns with just symbol (default amount)
                elif len(groups) == 1 and groups[0]:
                    symbol = groups[0].upper()
                    # Map common names to symbols
                    symbol_map = {
                        'BITCOIN': 'BTC',
                        'ETHEREUM': 'ETH',
                        'SOLANA': 'SOL',
                        'CARDANO': 'ADA'
                    }
                    symbol = symbol_map.get(symbol, symbol)

                    return {
                        'action': 'BUY',
                        'amount': 0.01,  # Default amount
                        'symbol': symbol,
                        'needs_confirmation': True,
                        'original_message': message
                    }

        # Check sell patterns
        for pattern in sell_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()

                # Handle "sell it" case
                if 'sell it' in message or 'dump it' in message:
                    return {
                        'action': 'SELL',
                        'amount': 'ALL',
                        'symbol': 'BTC',  # Default to BTC
                        'needs_confirmation': True,
                        'original_message': message
                    }

                # Handle "sell all" patterns
                if 'all' in pattern and len(groups) == 1:
                    symbol = groups[0].upper()
                    return {
                        'action': 'SELL',
                        'amount': 'ALL',
                        'symbol': symbol
                    }

                # Handle patterns with amount and symbol
                elif len(groups) == 2 and groups[0] and groups[1]:
                    try:
                        amount = float(groups[0])
                        symbol = groups[1].upper()
                        return {
                            'action': 'SELL',
                            'amount': amount,
                            'symbol': symbol
                        }
                    except ValueError:
                        continue

                # Handle patterns with just symbol
                elif len(groups) == 1 and groups[0]:
                    symbol = groups[0].upper()
                    symbol_map = {
                        'BITCOIN': 'BTC',
                        'ETHEREUM': 'ETH',
                        'SOLANA': 'SOL',
                        'CARDANO': 'ADA'
                    }
                    symbol = symbol_map.get(symbol, symbol)

                    return {
                        'action': 'SELL',
                        'amount': 'ALL',  # Default to sell all
                        'symbol': symbol,
                        'needs_confirmation': True,
                        'original_message': message
                    }

        return None
