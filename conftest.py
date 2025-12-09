"""
Ensure repository root is on sys.path so tests can import local packages
Used to run pytest
"""

import os
import sys


# Ensure repository root is on sys.path so tests can import local packages
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
