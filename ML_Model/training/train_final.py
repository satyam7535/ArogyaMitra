"""
ArogyaMitra — Final Model Training (Production Command)
Dispatches to train_and_export_v2 (Bernoulli Naive Bayes + Exact Bayesian Log-Odds)
Exports versioned artifacts to ML_Model/model/v2/ and root ML_Model/model/.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ML_Model.training.train_v2_naive_bayes import train_and_export_v2

if __name__ == "__main__":
    train_and_export_v2()
