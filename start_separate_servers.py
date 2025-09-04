#!/usr/bin/env python3
"""
🚀 Separate Server Launcher
Starts frontend (port 3000) and backend (port 5001) with enhanced logging
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 ALIBABA CRYPTO TRADING - SEPARATE SERVERS")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🖥️  Frontend Server: http://localhost:3000 (Enhanced UI + Logs)")
    print("🔧 Backend Server:  http://localhost:5001 (Trading API)")
    print("=" * 80)

def check_files():
    """Check if required files exist"""
    required_files = [
        'frontend_server.py',
        'backend_server.py', 
        'frontend_ode.py',
        'crypto_trading_engine.py'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print("❌ Missing files:")
        for file in missing:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def start_backend():
    """Start backend server"""
    try:
        print("🔧 Starting Backend Server (Port 5001)...")
        
        backend_process = subprocess.Popen([
            sys.executable, 'backend_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
           universal_newlines=True, bufsize=1)
        
        # Give it time to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend Server started successfully")
            print("📡 Trading API: http://localhost:5001")
            return backend_process
        else:
            print("❌ Backend Server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Backend startup error: {e}")
        return None

def start_frontend():
    """Start frontend server"""
    try:
        print("🖥️  Starting Frontend Server (Port 3000)...")
        
        frontend_process = subprocess.Popen([
            sys.executable, 'frontend_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
           universal_newlines=True, bufsize=1)
        
        # Give it time to start
        time.sleep(3)
        
        if frontend_process.poll() is None:
            print("✅ Frontend Server started successfully")
            print("🌐 Dashboard: http://localhost:3000")
            return frontend_process
        else:
            print("❌ Frontend Server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Frontend startup error: {e}")
        return None

def open_browser():
    """Open frontend in browser"""
    try:
        time.sleep(4)
        print("🌐 Opening frontend dashboard...")
        webbrowser.open('http://localhost:3000')
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")

def monitor_processes(backend_process, frontend_process):
    """Monitor both processes"""
    print("\n📊 SERVERS RUNNING")
    print("=" * 50)
    print("🔧 Backend:  http://localhost:5001")
    print("🖥️  Frontend: http://localhost:3000")
    print("📝 Logs: backend.log, frontend.log")
    print("=" * 50)
    print("💡 Tips:")
    print("   - Use frontend for enhanced UI and logging")
    print("   - Check log files for detailed debugging")
    print("   - Try: 'buy 0.01 BTC', 'show portfolio'")
    print("=" * 50)
    print("Press Ctrl+C to stop both servers")
    
    try:
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            backend_running = backend_process.poll() is None
            frontend_running = frontend_process.poll() is None
            
            if not backend_running:
                print("❌ Backend server stopped unexpectedly")
                break
                
            if not frontend_running:
                print("❌ Frontend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested...")
        
        # Stop processes
        if backend_process.poll() is None:
            print("🔄 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()
            
        if frontend_process.poll() is None:
            print("🔄 Stopping frontend server...")
            frontend_process.terminate()
            frontend_process.wait()
        
        print("📊 Both servers stopped")

def main():
    """Main launcher"""
    print_banner()
    
    # Check files
    if not check_files():
        input("\nPress Enter to exit...")
        return
    
    print("\n🔄 Starting servers...")
    
    # Start backend first
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot continue without backend server")
        input("Press Enter to exit...")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Cannot continue without frontend server")
        backend_process.terminate()
        input("Press Enter to exit...")
        return
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Monitor both processes
    monitor_processes(backend_process, frontend_process)

if __name__ == "__main__":
    main()
