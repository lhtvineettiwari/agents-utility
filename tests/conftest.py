"""
PyTest configuration file for YouTube Tracker tests
"""
import pytest
import os
import sys

# Add src directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
