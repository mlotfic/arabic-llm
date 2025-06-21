# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 21:36:01 2025

@author: m
"""

import os
import json
import pandas as pd
    
def to_csv(df, csv_path):
    """Save DF to file with proper encoding for Arabic text"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


directory_path = "output/info"
files = os.listdir(directory_path)

file_path = os.path.join(directory_path, "info_editions.csv")
# Read the CSV file
df = pd.read_csv(file_path, encoding='utf-8')