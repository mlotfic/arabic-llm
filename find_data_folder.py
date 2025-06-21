# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 21:33:55 2025

@author: m
"""

from pathlib import Path

def find_data_folder(start_path: Path = None) -> Path:
    """
    Walks up the directory tree from the start_path (defaults to current file)
    and returns the first found folder named 'data'.
    """
    current = start_path or Path(__file__).resolve().parent

    while current != current.parent:
        data_folder = current / 'data'
        if data_folder.is_dir():
            return data_folder
        current = current.parent

    return None  # Not found

if __name__ == "__main__":
    data_path = find_data_folder()
    print("Found data folder:", data_path or "Not found")

