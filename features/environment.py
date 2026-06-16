"""What behave needs to know before it runs anything.

The board's button runs one feature file from wherever the board happens to be, so the
repository root goes on the path here rather than being assumed to be the working
directory.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
