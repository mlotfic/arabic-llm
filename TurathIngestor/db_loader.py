# db_loader.py
import sqlite3

def connect_db(path='data/turath.db'):
    return sqlite3.connect(path)
