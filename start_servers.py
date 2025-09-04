#!/usr/bin/env python3
"""
🚀 Server Startup Script
Starts both backend (port 8000) and Gradio frontend (port 3000)
"""

import os
import sys
import time
import subprocess
import signal
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - STARTUP - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def start_backend():
    """Start the backend server"""
    logger.info("🔧 Starting backend server on port 8000...")
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "backend_server.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        logger.info("✅ Backend server started")
        return backend_process
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        return None

def start_gradio_frontend():
    """Start the Gradio frontend"""
    logger.info("🌐 Starting Gradio frontend on port 3000...")
    try:
        frontend_process = subprocess.Popen(
            [sys.executable, "gradio_frontend.py"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        logger.info("✅ Gradio frontend started")
        return frontend_process
    except Exception as e:
        logger.error(f"❌ Failed to start Gradio frontend: {e}")
        return None

def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("🚀 ALIBABA AI CRYPTO CHATBOT - SERVER STARTUP")
    logger.info("=" * 60)
    logger.info(f"📅 Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📂 Working Directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    processes = []
    
    try:
        # Start backend server
        backend_process = start_backend()
        if backend_process:
            processes.append(("Backend", backend_process))
            time.sleep(3)  # Give backend time to start
        else:
            logger.error("❌ Cannot start without backend server")
            return
        
        # Start Gradio frontend
        frontend_process = start_gradio_frontend()
        if frontend_process:
            processes.append(("Gradio Frontend", frontend_process))
            time.sleep(2)  # Give frontend time to start
        
        if not processes:
            logger.error("❌ No servers started successfully")
            return
        
        logger.info("=" * 60)
        logger.info("🎉 ALL SERVERS STARTED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("📡 Backend API: http://localhost:8000")
        logger.info("🌐 Gradio Frontend: http://localhost:3000")
        logger.info("=" * 60)
        logger.info("💡 Open http://localhost:3000 in your browser to use the chatbot")
        logger.info("🛑 Press Ctrl+C to stop all servers")
        logger.info("=" * 60)
        
        # Monitor processes
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    logger.error(f"❌ {name} process died unexpectedly")
                    # Kill all other processes
                    for other_name, other_process in processes:
                        if other_process != process and other_process.poll() is None:
                            other_process.terminate()
                    return
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown signal received")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        
    finally:
        # Clean shutdown
        logger.info("🔄 Shutting down servers...")
        for name, process in processes:
            if process.poll() is None:
                logger.info(f"🛑 Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"✅ {name} stopped")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️  Force killing {name}...")
                    process.kill()
        
        logger.info("👋 All servers stopped. Goodbye!")

if __name__ == "__main__":
    main()
