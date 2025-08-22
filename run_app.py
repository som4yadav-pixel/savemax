#!/usr/bin/env python3
"""
Launcher script for SaveMax Streamlit app.
This script adds the current directory to Python path and runs the app.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Now import and run the app
from app.app import main

if __name__ == "__main__":
    main() 