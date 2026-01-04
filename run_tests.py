#!/usr/bin/env python3
"""
Quick test runner for stock-eda project.
Attempts to run pytest in the current environment or provides instructions.
"""

import subprocess
import sys
import os

def main():
    print("=" * 70)
    print("Stock EDA Test Suite")
    print("=" * 70)
    
    # Try to run pytest
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            check=False,
            capture_output=False
        )
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("\n❌ pytest not found in current environment")
        print("\nTo install pytest:")
        print("  1. Activate your virtual environment:")
        print("     Windows: .venv\\Scripts\\activate")
        print("     Mac/Linux: source .venv/bin/activate")
        print("\n  2. Install dev dependencies:")
        print("     pip install -e \".[dev]\"")
        print("\n  3. Run tests:")
        print("     pytest")
        sys.exit(1)

if __name__ == "__main__":
    main()
