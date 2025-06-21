# -*- coding: utf-8 -*-
"""
Created on Sun May 25 21:13:33 2025

@author: m
"""

import sqlite3
import redis
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, sqlite_db_path: str = "islamic_texts.db", 
                 redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """
        Initialize the database manager with SQLite and Redis connections.
        
        Args:
            sqlite_db_path: Path to SQLite database file
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
        """
        self.sqlite_db_path = sqlite_db_path
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        
        # Redis key prefixes for primary keys
        self.PK_PREFIX = "pk"
        self.TABLES = ["narrators", "hadith", "book"]
        
        # Initialize databases
        self._init_sqlite()
        self._load_primary_keys_to_redis()
    
    def _init_sqlite(self):
        """Create SQLite database and tables if they don't exist."""
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            # Create narrators table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS narrators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    biography TEXT,
                    birth_year INTEGER,
                    death_year INTEGER,
                    reliability_grade TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create book table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS book (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    publication_year INTEGER,
                    language TEXT DEFAULT 'Arabic',
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create hadith table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hadith (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    translation TEXT,
                    narrator_id INTEGER,
                    book_id INTEGER,
                    chapter TEXT,
                    hadith_number INTEGER,
                    authenticity_grade TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (narrator_id) REFERENCES narrators (id),
                    FOREIGN KEY (book_id) REFERENCES book (id)
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hadith_narrator ON hadith(narrator_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hadith_book ON hadith(book_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_narrator_name ON narrators(name)')
            
            conn.commit()
            logger.info("SQLite database and tables initialized successfully")
    
    @contextmanager
    def _get_sqlite_connection(self):
        """Context manager for SQLite connections."""
        conn = sqlite3.connect(self.sqlite_db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _load_primary_keys_to_redis(self):
        """Load all existing primary keys from SQLite to Redis."""
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            for table in self.TABLES:
                # Get all primary keys from the table
                cursor.execute(f"SELECT id FROM {table}")
                pks = [row[0] for row in cursor.fetchall()]
                
                # Store in Redis as a set
                redis_key = f"{self.PK_PREFIX}:{table}"
                if pks:
                    self.redis_client.sadd(redis_key, *pks)
                    logger.info(f"Loaded {len(pks)} primary keys for table '{table}' into Redis")
                else:
                    logger.info(f"No existing primary keys found for table '{table}'")
    
    def _get_next_available_id(self, table: str) -> int:
        """Get the next available ID for a table, checking both SQLite and Redis."""
        redis_key = f"{self.PK_PREFIX}:{table}"
        
        # Get existing IDs from Redis
        existing_ids = set(map(int, self.redis_client.smembers(redis_key)))
        
        # Find the next available ID
        next_id = 1
        while next_id in existing_ids:
            next_id += 1
        
        return next_id
    
    def _update_redis_pk(self, table: str, pk: int):
        """Add a primary key to Redis set."""
        redis_key = f"{self.PK_PREFIX}:{table}"
        self.redis_client.sadd(redis_key, pk)
    
    def _remove_redis_pk(self, table: str, pk: int):
        """Remove a primary key from Redis set."""
        redis_key = f"{self.PK_PREFIX}:{table}"
        self.redis_client.srem(redis_key, pk)
    
    def _pk_exists(self, table: str, pk: int) -> bool:
        """Check if a primary key exists in Redis."""
        redis_key = f"{self.PK_PREFIX}:{table}"
        return self.redis_client.sismember(redis_key, pk)
    
    def insert_narrator(self, name: str, biography: str = None, birth_year: int = None, 
                       death_year: int = None, reliability_grade: str = None) -> int:
        """Insert a new narrator record."""
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO narrators (name, biography, birth_year, death_year, reliability_grade)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, biography, birth_year, death_year, reliability_grade))
                
                narrator_id = cursor.lastrowid
                conn.commit()
                
                # Update Redis
                self._update_redis_pk("narrators", narrator_id)
                
                logger.info(f"Inserted narrator with ID {narrator_id}")
                return narrator_id
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to insert narrator: {e}")
                raise
    
    def insert_book(self, title: str, author: str, isbn: str = None, 
                   publication_year: int = None, language: str = "Arabic", category: str = None) -> int:
        """Insert a new book record."""
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO book (title, author, isbn, publication_year, language, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, author, isbn, publication_year, language, category))
                
                book_id = cursor.lastrowid
                conn.commit()
                
                # Update Redis
                self._update_redis_pk("book", book_id)
                
                logger.info(f"Inserted book with ID {book_id}")
                return book_id
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to insert book: {e}")
                raise
    
    def insert_hadith(self, text: str, translation: str = None, narrator_id: int = None,
                     book_id: int = None, chapter: str = None, hadith_number: int = None,
                     authenticity_grade: str = None) -> int:
        """Insert a new hadith record."""
        # Validate foreign keys
        if narrator_id and not self._pk_exists("narrators", narrator_id):
            raise ValueError(f"Narrator ID {narrator_id} does not exist")
        
        if book_id and not self._pk_exists("book", book_id):
            raise ValueError(f"Book ID {book_id} does not exist")
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO hadith (text, translation, narrator_id, book_id, chapter, hadith_number, authenticity_grade)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (text, translation, narrator_id, book_id, chapter, hadith_number, authenticity_grade))
                
                hadith_id = cursor.lastrowid
                conn.commit()
                
                # Update Redis
                self._update_redis_pk("hadith", hadith_id)
                
                logger.info(f"Inserted hadith with ID {hadith_id}")
                return hadith_id
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to insert hadith: {e}")
                raise
    
    def update_narrator(self, narrator_id: int, **kwargs) -> bool:
        """Update an existing narrator record."""
        if not self._pk_exists("narrators", narrator_id):
            logger.error(f"Narrator ID {narrator_id} does not exist")
            return False
        
        # Build dynamic update query
        allowed_fields = ['name', 'biography', 'birth_year', 'death_year', 'reliability_grade']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            logger.warning("No valid fields provided for update")
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [narrator_id]
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(f'''
                    UPDATE narrators 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                logger.info(f"Updated narrator ID {narrator_id}")
                return True
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to update narrator: {e}")
                return False
    
    def update_book(self, book_id: int, **kwargs) -> bool:
        """Update an existing book record."""
        if not self._pk_exists("book", book_id):
            logger.error(f"Book ID {book_id} does not exist")
            return False
        
        # Build dynamic update query
        allowed_fields = ['title', 'author', 'isbn', 'publication_year', 'language', 'category']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            logger.warning("No valid fields provided for update")
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [book_id]
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(f'''
                    UPDATE book 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                logger.info(f"Updated book ID {book_id}")
                return True
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to update book: {e}")
                return False
    
    def update_hadith(self, hadith_id: int, **kwargs) -> bool:
        """Update an existing hadith record."""
        if not self._pk_exists("hadith", hadith_id):
            logger.error(f"Hadith ID {hadith_id} does not exist")
            return False
        
        # Validate foreign keys if provided
        if 'narrator_id' in kwargs and kwargs['narrator_id'] and not self._pk_exists("narrators", kwargs['narrator_id']):
            raise ValueError(f"Narrator ID {kwargs['narrator_id']} does not exist")
        
        if 'book_id' in kwargs and kwargs['book_id'] and not self._pk_exists("book", kwargs['book_id']):
            raise ValueError(f"Book ID {kwargs['book_id']} does not exist")
        
        # Build dynamic update query
        allowed_fields = ['text', 'translation', 'narrator_id', 'book_id', 'chapter', 'hadith_number', 'authenticity_grade']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            logger.warning("No valid fields provided for update")
            return False
        
        set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [hadith_id]
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(f'''
                    UPDATE hadith 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', values)
                
                conn.commit()
                logger.info(f"Updated hadith ID {hadith_id}")
                return True
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to update hadith: {e}")
                return False
    
    def delete_record(self, table: str, record_id: int) -> bool:
        """Delete a record from the specified table."""
        if table not in self.TABLES:
            raise ValueError(f"Invalid table name: {table}")
        
        if not self._pk_exists(table, record_id):
            logger.error(f"Record ID {record_id} does not exist in table {table}")
            return False
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
                conn.commit()
                
                # Remove from Redis
                self._remove_redis_pk(table, record_id)
                
                logger.info(f"Deleted record ID {record_id} from table {table}")
                return True
                
            except sqlite3.Error as e:
                logger.error(f"Failed to delete record: {e}")
                return False
    
    def get_all_primary_keys(self, table: str) -> List[int]:
        """Get all primary keys for a table from Redis."""
        if table not in self.TABLES:
            raise ValueError(f"Invalid table name: {table}")
        
        redis_key = f"{self.PK_PREFIX}:{table}"
        return [int(pk) for pk in self.redis_client.smembers(redis_key)]
    
    def sync_redis_with_sqlite(self):
        """Synchronize Redis primary keys with SQLite database."""
        logger.info("Starting Redis-SQLite synchronization...")
        
        for table in self.TABLES:
            # Clear existing Redis keys
            redis_key = f"{self.PK_PREFIX}:{table}"
            self.redis_client.delete(redis_key)
            
            # Reload from SQLite
            with self._get_sqlite_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT id FROM {table}")
                pks = [row[0] for row in cursor.fetchall()]
                
                if pks:
                    self.redis_client.sadd(redis_key, *pks)
                
                logger.info(f"Synchronized {len(pks)} primary keys for table '{table}'")
        
        logger.info("Redis-SQLite synchronization completed")
    
    def get_record(self, table: str, record_id: int) -> Optional[Dict]:
        """Get a single record by ID."""
        if table not in self.TABLES:
            raise ValueError(f"Invalid table name: {table}")
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def search_records(self, table: str, **conditions) -> List[Dict]:
        """Search records with conditions."""
        if table not in self.TABLES:
            raise ValueError(f"Invalid table name: {table}")
        
        if not conditions:
            # Return all records if no conditions
            with self._get_sqlite_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table}")
                return [dict(row) for row in cursor.fetchall()]
        
        # Build WHERE clause
        where_clause = ' AND '.join([f"{field} = ?" for field in conditions.keys()])
        values = list(conditions.values())
        
        with self._get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}", values)
            return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close Redis connection."""
        self.redis_client.close()
        logger.info("Database connections closed")


# Example usage
if __name__ == "__main__":
    # Initialize the database manager
    db_manager = DatabaseManager()
    
    try:
        # Insert sample data
        narrator_id = db_manager.insert_narrator(
            name="Abu Hurairah",
            biography="Companion of Prophet Muhammad",
            reliability_grade="Trustworthy"
        )
        
        book_id = db_manager.insert_book(
            title="Sahih Bukhari",
            author="Imam Bukhari",
            category="Hadith Collection"
        )
        
        hadith_id = db_manager.insert_hadith(
            text="Actions are but by intention...",
            translation="The reward of deeds depends upon the intentions...",
            narrator_id=narrator_id,
            book_id=book_id,
            authenticity_grade="Sahih"
        )
        
        # Update records
        db_manager.update_narrator(narrator_id, biography="Companion and narrator of hadith")
        
        # Search records
        narrators = db_manager.search_records("narrators", reliability_grade="Trustworthy")
        print(f"Found {len(narrators)} trustworthy narrators")
        
        # Get primary keys
        all_hadith_ids = db_manager.get_all_primary_keys("hadith")
        print(f"All hadith IDs in Redis: {all_hadith_ids}")
        
        # Sync Redis with SQLite
        db_manager.sync_redis_with_sqlite()
        
    finally:
        db_manager.close()