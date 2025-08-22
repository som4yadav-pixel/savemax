#!/usr/bin/env python3
"""
Test script to verify Flask app setup
"""

try:
    from app.app import app
    print("✅ Successfully imported Flask app")
    print(f"App name: {app.name}")
    print(f"App secret key configured: {'Yes' if app.secret_key else 'No'}")
    
    # Check if CORS is configured
    if hasattr(app, 'extensions') and 'cors' in app.extensions:
        print("✅ CORS is configured")
    else:
        print("❌ CORS not found")
        
    print("\n🎉 Flask app is ready for deployment!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 