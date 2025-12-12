"""
Database module for managing book metadata with SQLite
"""
import sqlite3
import json
import aiosqlite
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

DB_PATH = "books.db"


def initialize_database(db_path: str = DB_PATH):
    """
    Initialize SQLite database with schema
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT,
            publisher TEXT,
            image_path TEXT NOT NULL,
            embedding_vector BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on title and author for search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_books_author ON books(author)
    """)
    
    # Create metadata table for system info
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {db_path}")


def migrate_from_json(json_path: str = "meta.json", db_path: str = DB_PATH):
    """
    Migrate existing meta.json data to SQLite database
    """
    try:
        with open(json_path, 'r') as f:
            meta = json.load(f)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        migrated_count = 0
        for book_id, book_data in meta.items():
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO books 
                    (book_id, title, author, isbn, publisher, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    book_id,
                    book_data.get('title', ''),
                    book_data.get('author', ''),
                    book_data.get('isbn'),
                    book_data.get('publisher'),
                    book_data.get('image', '')
                ))
                migrated_count += 1
            except Exception as e:
                logger.error(f"Failed to migrate book {book_id}: {e}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Migrated {migrated_count} books from {json_path} to {db_path}")
        return migrated_count
    except FileNotFoundError:
        logger.warning(f"No existing {json_path} file found for migration")
        return 0
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


class BookDatabase:
    """Async database interface for books"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    async def get_book(self, book_id: str) -> Optional[Dict]:
        """Get a single book by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT book_id, title, author, isbn, publisher, image_path FROM books WHERE book_id = ?",
                (book_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'book_id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'isbn': row[3],
                        'publisher': row[4],
                        'image': row[5]
                    }
                return None
    
    async def get_all_books(self, limit: int = None, offset: int = 0) -> List[Dict]:
        """Get all books with optional pagination"""
        query = "SELECT book_id, title, author, isbn, publisher, image_path FROM books ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'book_id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'isbn': row[3],
                        'publisher': row[4],
                        'image': row[5]
                    }
                    for row in rows
                ]
    
    async def add_book(self, book_id: str, title: str, author: str, 
                       image_path: str, isbn: str = None, publisher: str = None) -> bool:
        """Add a new book"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO books (book_id, title, author, isbn, publisher, image_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (book_id, title, author, isbn, publisher, image_path))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to add book {book_id}: {e}")
            return False
    
    async def update_book(self, book_id: str, **kwargs) -> bool:
        """Update book metadata"""
        allowed_fields = ['title', 'author', 'isbn', 'publisher', 'image_path']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [book_id]
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f"UPDATE books SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE book_id = ?",
                    values
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update book {book_id}: {e}")
            return False
    
    async def delete_book(self, book_id: str) -> bool:
        """Delete a book"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to delete book {book_id}: {e}")
            return False
    
    async def count_books(self) -> int:
        """Get total number of books"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM books") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Search books by title or author"""
        search_query = f"%{query}%"
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT book_id, title, author, isbn, publisher, image_path 
                FROM books 
                WHERE title LIKE ? OR author LIKE ?
                ORDER BY title
                LIMIT ?
            """, (search_query, search_query, limit)) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        'book_id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'isbn': row[3],
                        'publisher': row[4],
                        'image': row[5]
                    }
                    for row in rows
                ]


def get_all_books_sync(db_path: str = DB_PATH) -> Dict[str, Dict]:
    """
    Synchronous version for backward compatibility
    Returns data in old meta.json format
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT book_id, title, author, isbn, publisher, image_path FROM books"
    )
    
    books = {}
    for row in cursor.fetchall():
        book_data = {
            'title': row[1],
            'author': row[2],
            'image': row[5]
        }
        if row[3]:  # isbn
            book_data['isbn'] = row[3]
        if row[4]:  # publisher
            book_data['publisher'] = row[4]
        
        books[row[0]] = book_data
    
    conn.close()
    return books


def get_book_ids_sync(db_path: str = DB_PATH) -> List[str]:
    """Get all book IDs synchronously"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT book_id FROM books ORDER BY created_at")
    book_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return book_ids


# Initialize database on module import
try:
    initialize_database()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

