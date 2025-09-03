import gradio as gr
import pandas as pd
import sqlite3
import requests
from datetime import datetime

class PaperTradingSystem:
    def __init__(self, initial_balance=10000):
        self.initial_balance = initial_balance
        self.setup_database()
    
    def setup_database(self):
        conn = sqlite3.connect('trading.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                price REAL,
                value REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                symbol TEXT PRIMARY KEY,
                quantity REAL,
                avg_price REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance (
                cash REAL,
                total_value REAL
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM balance')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO balance VALUES (?, ?)', 
                         (self.initial_balance, self.initial_balance))
        
        conn.commit()
        conn.close()
    
    def get_current_price(self, symbol):
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            return float(response.json()['price'])
        except:
            return 50000
    
    def execute_trade(self, symbol, side, quantity):
        current_price = self.get_current_price(symbol)
        value = quantity * current_price
        
        conn = sqlite3.connect('trading.db')
        cursor = conn.cursor()
        
        if side.upper() == "BUY":
            cursor.execute('SELECT cash FROM balance')
            cash = cursor.fetchone()[0]
            
            if cash >= value:
                cursor.execute('''
                    INSERT INTO trades (timestamp, symbol, side, quantity, price, value)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now(), symbol, side, quantity, current_price, value))
                
                cursor.execute('SELECT quantity, avg_price FROM portfolio WHERE symbol = ?', (symbol,))
                existing = cursor.fetchone()
                
                if existing:
                    total_qty = existing[0] + quantity
                    avg_price = ((existing[0] * existing[1]) + value) / total_qty
                    cursor.execute('UPDATE portfolio SET quantity = ?, avg_price = ? WHERE symbol = ?',
                                 (total_qty, avg_price, symbol))
                else:
                    cursor.execute('INSERT INTO portfolio VALUES (?, ?, ?)',
                                 (symbol, quantity, current_price))
                
                cursor.execute('UPDATE balance SET cash = cash - ?', (value,))
                conn.commit()
                status = f"✅ Bought {quantity} {symbol} at ${current_price:.2f}"
            else:
                status = "❌ Insufficient funds"
        
        else:  # SELL
            cursor.execute('SELECT quantity FROM portfolio WHERE symbol = ?', (symbol,))
            holdings = cursor.fetchone()
            
            if holdings and holdings[0] >= quantity:
                cursor.execute('''
                    INSERT INTO trades (timestamp, symbol, side, quantity, price, value)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (datetime.now(), symbol, side, quantity, current_price, value))
                
                cursor.execute('UPDATE portfolio SET quantity = quantity - ? WHERE symbol = ?',
                             (quantity, symbol))
                cursor.execute('UPDATE balance SET cash = cash + ?', (value,))
                conn.commit()
                status = f"✅ Sold {quantity} {symbol} at ${current_price:.2f}"
            else:
                status = "❌ Insufficient holdings"
        
        conn.close()
        return status
    
    def get_portfolio(self):
        conn = sqlite3.connect('trading.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT symbol, quantity, avg_price FROM portfolio WHERE quantity > 0')
        positions = cursor.fetchall()
        
        portfolio_data = []
        total_invested = 0
        total_current = 0
        
        for symbol, quantity, avg_price in positions:
            current_price = self.get_current_price(symbol)
            invested = quantity * avg_price
            current_value = quantity * current_price
            pnl = current_value - invested
            pnl_pct = (pnl / invested) * 100 if invested > 0 else 0
            
            portfolio_data.append({
                'Symbol': symbol,
                'Quantity': f"{quantity:.8f}",
                'Avg Price': f"${avg_price:.2f}",
                'Current Price': f"${current_price:.2f}",
                'Invested': f"${invested:.2f}",
                'Current Value': f"${current_value:.2f}",
                'P&L': f"${pnl:.2f}",
                'P&L %': f"{pnl_pct:.2f}%"
            })
            
            total_invested += invested
            total_current += current_value
        
        cursor.execute('SELECT cash FROM balance')
        cash = cursor.fetchone()[0]
        
        total_pnl = total_current + cash - self.initial_balance
        total_pnl_pct = (total_pnl / self.initial_balance) * 100
        
        portfolio_data.append({
            'Symbol': '📊 TOTAL PORTFOLIO',
            'Quantity': f"Cash: ${cash:.2f}",
            'Avg Price': '',
            'Current Price': '',
            'Invested': f"${self.initial_balance:.2f}",
            'Current Value': f"${total_current + cash:.2f}",
            'P&L': f"${total_pnl:.2f}",
            'P&L %': f"{total_pnl_pct:.2f}%"
        })
        
        conn.close()
        return pd.DataFrame(portfolio_data)
    
    def get_trade_history(self):
        conn = sqlite3.connect('trading.db')
        df = pd.read_sql_query('SELECT * FROM trades ORDER BY timestamp DESC', conn)
        conn.close()
        return df

trading_system = PaperTradingSystem()

def create_chart_iframe(symbol="BTCUSD"):
    """Single TradingView chart iframe"""
    symbol_map = {
        "BTCUSD": "BITSTAMP:BTCUSD",
        "ETHUSD": "BITSTAMP:ETHUSD", 
        "ADAUSD": "BINANCE:ADAUSDT",
        "SOLUSD": "COINBASE:SOLUSD"
    }
    
    tv_symbol = symbol_map.get(symbol, "BITSTAMP:BTCUSD")
    
    html = f"""
    <iframe 
        src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol={tv_symbol}&interval=15&hidesidetoolbar=0&hidetoptoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=Etc%2FUTC&locale=en" 
        width="100%" 
        height="600" 
        frameborder="0" 
        allowtransparency="true" 
        scrolling="no">
    </iframe>
    """
    return html

def create_crypto_app():
    with gr.Blocks(title="🚀 Crypto Trading Dashboard", theme=gr.themes.Monochrome()) as app:
        
        gr.Markdown("# 🚀 Professional Crypto Trading Dashboard")
        gr.Markdown("*Live TradingView charts with paper trading simulation*")
        
        with gr.Tab("📈 Live Chart"):
            with gr.Row():
                symbol_select = gr.Dropdown(
                    label="Select Cryptocurrency",
                    choices=["BTCUSD", "ETHUSD", "ADAUSD", "SOLUSD"],
                    value="BTCUSD"
                )
                refresh_chart_btn = gr.Button("🔄 Update Chart", variant="primary")
            
            # Single chart only
            price_chart = gr.HTML(
                value=create_chart_iframe(),
                label="TradingView Live Chart"
            )
        
        with gr.Tab("💼 Paper Trading"):
            with gr.Row():
                gr.Markdown("### Execute Trade")
            
            with gr.Row():
                trade_symbol = gr.Textbox(label="Symbol", value="BTCUSDT")
                trade_side = gr.Radio(label="Side", choices=["BUY", "SELL"], value="BUY")
                trade_quantity = gr.Number(label="Quantity", value=0.1, precision=8)
                execute_btn = gr.Button("🚀 Execute Trade", variant="primary")
            
            trade_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Portfolio")
            
            portfolio_table = gr.Dataframe(
                headers=["Symbol", "Quantity", "Avg Price", "Current Price", "Invested", "Current Value", "P&L", "P&L %"],
                interactive=False,
                max_height=400
            )
        
        with gr.Tab("📊 Trade History"):
            history_table = gr.Dataframe(
                headers=["ID", "Timestamp", "Symbol", "Side", "Quantity", "Price", "Value"],
                interactive=False,
                max_height=500
            )
        
        # Event handlers
        def update_chart(symbol):
            return create_chart_iframe(symbol)
        
        def execute_trade(symbol, side, quantity):
            status = trading_system.execute_trade(symbol, side, quantity)
            portfolio = trading_system.get_portfolio()
            history = trading_system.get_trade_history()
            return status, portfolio, history
        
        def refresh_data():
            portfolio = trading_system.get_portfolio()
            history = trading_system.get_trade_history()
            return portfolio, history
        
        # Wire up the interface
        refresh_chart_btn.click(update_chart, inputs=[symbol_select], outputs=[price_chart])
        execute_btn.click(execute_trade, inputs=[trade_symbol, trade_side, trade_quantity], outputs=[trade_status, portfolio_table, history_table])
        refresh_btn.click(refresh_data, outputs=[portfolio_table, history_table])
        
        # Load initial data
        app.load(refresh_data, outputs=[portfolio_table, history_table])
    
    return app

if __name__ == "__main__":
    app = create_crypto_app()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
        share=False
    )
