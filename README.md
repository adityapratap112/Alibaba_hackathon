# 🤖 Alibaba AI Crypto Chatbot - JSON API

A **JSON-serializable** crypto chatbot powered by Alibaba Cloud AI with real-time market data integration. Perfect for frontend applications, web APIs, and mobile apps.

## ✨ Features

- **🔥 JSON-First Design**: All responses are JSON-serializable for easy frontend integration
- **🤖 Alibaba Cloud AI**: Powered by Qwen-Plus model for intelligent crypto analysis
- **📊 Real-Time Data**: Live crypto prices from Binance (primary) and CoinGecko (fallback)
- **💬 Session Management**: Isolated chat sessions with persistent history
- **🌐 Frontend Ready**: Clean API methods for web/mobile integration
- **⚡ Fast & Reliable**: Automatic fallback systems and error handling

## 🚀 Quick Start

### 1. Installation

```bash
pip install requests python-dotenv flask flask-cors
```

### 2. Environment Setup

Create a `.env` file:
```env
ALIBABA_API_KEY=your_alibaba_api_key_here
```

### 3. Basic Usage

```python
from alibaba_crypto_chatbot import CryptoChatbotAPI

# Create a chatbot session
chatbot = CryptoChatbotAPI()

# Check status
status = chatbot.get_status()
print(status)  # JSON response

# Send a message
response = chatbot.send_message("What's the Bitcoin price?")
print(response)  # JSON response with AI analysis

# Get crypto price directly
price = chatbot.get_crypto_price("BTC")
print(price)  # JSON response with live price data
```

## 📋 API Reference

### Core Methods

#### `CryptoChatbotAPI()`
Creates a new chatbot session.

#### `send_message(message: str) -> dict`
Send a message and get AI response with context.

**Response Format:**
```json
{
  "success": true,
  "response": "AI analysis text...",
  "timestamp": "2025-09-04T09:45:29.974919",
  "session_id": "20250904_094529",
  "model": "qwen-plus",
  "provider": "Alibaba Cloud"
}
```

#### `get_crypto_price(symbol: str) -> dict`
Get real-time crypto price data.

**Response Format:**
```json
{
  "success": true,
  "symbol": "BTC",
  "current_price": 110637.35,
  "price_change_24h": -0.1,
  "volume_24h": 1300784278.66,
  "high_24h": 112575.27,
  "low_24h": 110528.71,
  "timestamp": "2025-09-04T09:45:30.266574",
  "source": "Binance"
}
```

#### `get_status() -> dict`
Get chatbot session status.

#### `get_chat_history(limit=None) -> dict`
Get chat history (optionally limited).

#### `clear_chat_history() -> dict`
Clear chat history for the session.

## 🌐 Web API Integration

### Flask API Example

Run the included Flask API:

```bash
python flask_api_example.py
```

**Available Endpoints:**
- `POST /api/session/create` - Create new session
- `POST /api/session/{id}/message` - Send message
- `GET /api/session/{id}/history` - Get chat history
- `GET /api/crypto/price/{symbol}` - Get crypto price
- `GET /api/health` - Health check

### Frontend Integration Example

```javascript
// Create session
const sessionResponse = await fetch('/api/session/create', {
    method: 'POST'
});
const session = await sessionResponse.json();

// Send message
const messageResponse = await fetch(`/api/session/${session.api_session_id}/message`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: 'Analyze Bitcoin for me'})
});
const result = await messageResponse.json();

console.log(result.response); // AI analysis
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python frontend_example.py
```

This will demonstrate:
- ✅ Session creation and management
- ✅ Real-time crypto price fetching
- ✅ AI chat interactions with context
- ✅ Chat history management
- ✅ Error handling scenarios
- ✅ Multi-user session isolation

## 💰 Supported Cryptocurrencies

- **BTC** (Bitcoin)
- **ETH** (Ethereum)
- **SOL** (Solana)
- **ADA** (Cardano)
- **MATIC** (Polygon)
- **LINK** (Chainlink)
- **AVAX** (Avalanche)
- **DOT** (Polkadot)

## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │  CryptoChatbot   │    │  Alibaba Cloud  │
│   (React/Vue)   │◄──►│      API         │◄──►│      AI         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Market Data     │
                       │  (Binance/       │
                       │   CoinGecko)     │
                       └──────────────────┘
```

## 📁 Project Structure

```
├── alibaba_crypto_chatbot.py    # Main chatbot with JSON API
├── frontend_example.py          # Usage examples and tests
├── flask_api_example.py         # Flask REST API wrapper
├── README.md                    # This documentation
└── .env                         # Environment variables
```

## 🛠️ Integration Tips

1. **Session Management**: Create one `CryptoChatbotAPI()` instance per user session
2. **Error Handling**: Always check the `success` field in responses
3. **Performance**: Use `get_crypto_price()` for quick price lookups without AI context
4. **Context**: The AI automatically maintains conversation context within sessions
5. **Scalability**: For production, store sessions in Redis or a database instead of memory

## 🔒 Security Notes

- Store your `ALIBABA_API_KEY` securely
- Implement rate limiting for production APIs
- Validate all user inputs before processing
- Use HTTPS in production environments

## 📊 Response Format

All API methods return consistent JSON responses:

```json
{
  "success": boolean,
  "data": "...",           // On success
  "error": "...",          // On failure
  "timestamp": "ISO string",
  "session_id": "string"
}
```

## 🚀 Production Deployment

For production use:

1. **Database**: Replace in-memory session storage with Redis/PostgreSQL
2. **Authentication**: Add user authentication and session validation
3. **Rate Limiting**: Implement API rate limiting
4. **Monitoring**: Add logging and monitoring
5. **Caching**: Cache crypto prices to reduce API calls
6. **Load Balancing**: Use multiple instances behind a load balancer

---

**Ready to integrate?** Check out `frontend_example.py` for complete usage examples! 🎯


