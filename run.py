#!/usr/bin/env python3
"""
File Renamer Application Launcher

This script provides a convenient way to launch the File Renamer application
from anywhere in the system.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run the main application
from src.main import main

if __name__ == "__main__":
    main()
