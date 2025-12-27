"""
Student Rating System - Main Application Launcher
Starts the web application interface
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import plotly
        import pandas
        import groq
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e.name}")
        print("\n📦 Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_webapp.txt"])
        return True

def create_directories():
    """Create necessary directories"""
    for directory in ["logs", "models", "data"]:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main application entry point"""
    print("=" * 70)
    print("🎓 STUDENT RATING SYSTEM".center(70))
    print("=" * 70)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("🚀 Starting web application...")
    print()
    print("📱 The app will open in your browser at:")
    print("   http://localhost:8501")
    print()
    print("💡 Features available:")
    print("   • Upload CSV report cards (auto-scans data/ folder)")
    print("   • Manual student data entry")
    print("   • Batch analysis for multiple students")
    print("   • Interactive visualizations")
    print("   • AI-powered recommendations (if GROQ_API_KEY set)")
    print()
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    # Start streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "webapp.py",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped. Thank you for using Student Rating System!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\n💡 Try running manually: streamlit run webapp.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
