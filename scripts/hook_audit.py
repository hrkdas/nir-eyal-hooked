#!/usr/bin/env python3
"""
Executable script for running HookEngine audits from anywhere.
"""
import sys
from pathlib import Path

# Add project root to sys.path so hook_engine is always importable
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from hook_engine.cli import main

if __name__ == "__main__":
    sys.exit(main())
