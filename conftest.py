import os
import sys

root = os.path.dirname(os.path.abspath(__file__))
for folder in ["ML_Model", "graph", "ui"]:
    p = os.path.join(root, folder)
    if p not in sys.path:
        sys.path.insert(0, p)

