#!/usr/bin/env python3
"""
🧪 Server Test Script
Tests backend and frontend connectivity
"""

import requests
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - TEST - %(message)s')
logger = logging.getLogger(__name__)

def test_backend():
    """Test backend server health"""
    logger.info("🔧 Testing backend server at http://localhost:8000...")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✅ Backend server is healthy")
                logger.info(f"   Server: {data.get('server')}")
                logger.info(f"   Version: {data.get('version')}")
                logger.info(f"   Trading: {'✅' if data.get('trading_available') else '❌'}")
                return True
            else:
                logger.error(f"❌ Backend unhealthy: {data}")
                return False
        else:
            logger.error(f"❌ Backend HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to backend - is it running?")
        return False
    except Exception as e:
        logger.error(f"❌ Backend test error: {e}")
        return False

def test_frontend():
    """Test frontend server"""
    logger.info("🌐 Testing Gradio frontend at http://localhost:3000...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ Gradio frontend is accessible")
            return True
        else:
            logger.error(f"❌ Frontend HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to frontend - is it running?")
        return False
    except Exception as e:
        logger.error(f"❌ Frontend test error: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("🧪 TESTING ALIBABA AI CRYPTO CHATBOT SERVERS")
    logger.info("=" * 50)
    logger.info(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    backend_ok = test_backend()
    time.sleep(1)
    frontend_ok = test_frontend()
    
    logger.info("=" * 50)
    if backend_ok and frontend_ok:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("💡 You can now use the chatbot at http://localhost:3000")
    else:
        logger.error("❌ SOME TESTS FAILED!")
        if not backend_ok:
            logger.error("   - Backend server issues")
        if not frontend_ok:
            logger.error("   - Frontend server issues")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
