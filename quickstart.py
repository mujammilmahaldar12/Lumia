#!/usr/bin/env python3
"""
Quick startup script for testing the Lumia system.

This script helps users quickly test the core functionality:
1. Validates configuration
2. Starts the API server
3. Optionally runs a quick data collection test
4. Shows how to access the Streamlit UI

Usage:
    python quickstart.py --help
    python quickstart.py --test-api
    python quickstart.py --full-demo
"""

import argparse
import subprocess
import sys
import time
import requests
from pathlib import Path


def print_banner():
    """Print a welcome banner."""
    print("""
🚀 ===================================== 🚀
    Lumia AI Financial Analytics System
🚀 ===================================== 🚀

Welcome to your AI-powered portfolio recommendation system!
    """)


def check_requirements():
    """Check if basic requirements are met."""
    print("📋 Checking requirements...")
    
    # Check if .env exists
    if not Path('.env').exists():
        if Path('.env.sample').exists():
            print("⚠️  .env file not found. Creating from sample...")
            import shutil
            shutil.copy('.env.sample', '.env')
            print("✅ Created .env file. Please update it with your settings.")
        else:
            print("❌ No .env file found. Please create one with your configuration.")
            return False
    
    # Check database
    try:
        from database import get_db
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text('SELECT 1'))
        db.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False
    
    print("✅ Basic requirements check passed")
    return True


def test_api_server(port=8000):
    """Test the API server functionality."""
    print(f"🚀 Starting API server on port {port}...")
    
    try:
        # Start the server in background
        import uvicorn
        from app.main import app
        
        print(f"📡 API server starting at http://localhost:{port}")
        print("🏥 Health endpoint: http://localhost:{port}/api/recommend/health")
        print("📚 API docs: http://localhost:{port}/docs")
        
        # Run server
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 API server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return False
    
    return True


def run_quick_demo():
    """Run a quick demonstration of the system."""
    print("🎯 Running quick system demonstration...")
    
    try:
        # Test news collection (just a few articles)
        print("📰 Testing news collection...")
        result = subprocess.run([
            sys.executable, "scripts/collect_news.py", 
            "--general", "--limit", "5"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ News collection test successful")
        else:
            print(f"⚠️ News collection test failed: {result.stderr}")
        
        # Test sentiment processing
        print("🤖 Testing sentiment processing...")
        result = subprocess.run([
            sys.executable, "scripts/process_sentiment.py",
            "--unprocessed", "--batch-size", "3", "--max-articles", "5"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Sentiment processing test successful")
        else:
            print(f"⚠️ Sentiment processing test failed: {result.stderr}")
        
        # Show system status
        print("📊 Checking system status...")
        result = subprocess.run([
            sys.executable, "start_scheduler.py", "status"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ System status check successful")
            print(result.stdout)
        else:
            print(f"⚠️ Status check failed: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("⏰ Demo operations timed out")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


def show_next_steps():
    """Show users what they can do next."""
    print("""
🎉 ================================ 🎉
       Lumia System Ready!
🎉 ================================ 🎉

Next Steps:

1. 🖥️  Start the API Server:
   python quickstart.py --api-only
   
2. 🎨 Launch the Test UI:
   streamlit run app/test_ui.py --server.port 8501
   
3. 🤖 Start Full Automation:
   python start_scheduler.py start
   
4. 📊 Test Portfolio Recommendations:
   curl -X POST "http://localhost:8000/api/recommend" \\
   -H "Content-Type: application/json" \\
   -d '{"capital": 10000, "risk": 0.5, "horizon_years": 5}'

🔗 Useful URLs:
   • API Documentation: http://localhost:8000/docs
   • Health Check: http://localhost:8000/api/recommend/health
   • Test UI: http://localhost:8501

📚 Documentation:
   • System Guide: README.md
   • Scripts Help: scripts/README.md
   • Configuration: .env file

🛠️ Troubleshooting:
   • Check Status: python start_scheduler.py status
   • View Logs: tail -f logs/scheduler.log
   • Test Jobs: python start_scheduler.py test-job collect_news

Happy trading with AI! 🚀📈
    """)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Lumia System Quick Start",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--test-api', 
        action='store_true',
        help='Start API server for testing'
    )
    parser.add_argument(
        '--full-demo',
        action='store_true', 
        help='Run complete demonstration with data collection'
    )
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Start only the API server'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for API server (default: 8000)'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Always check requirements first
    if not check_requirements():
        print("❌ Requirements check failed. Please fix the issues above.")
        return 1
    
    # Run requested operations
    if args.test_api or args.api_only:
        return 0 if test_api_server(args.port) else 1
    
    elif args.full_demo:
        run_quick_demo()
        show_next_steps()
        return 0
    
    else:
        # Default: just show what's available
        show_next_steps()
        return 0


if __name__ == '__main__':
    exit(main())