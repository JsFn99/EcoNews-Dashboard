# models/user.py
import sqlite3
import hashlib
import os
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at=None, active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self._active = active  # Use private attribute to avoid conflict with Flask-Login

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        """Override Flask-Login's is_active property"""
        return self._active

    def set_active(self, active):
        """Method to set active status"""
        self._active = active

    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash


class UserManager:
    def __init__(self, db_path='../Bmce_News.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with users table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           username
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           email
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password_hash
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           is_active
                           BOOLEAN
                           DEFAULT
                           1
                       )
                       ''')

        # Create favorites table for user articles
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS user_favorites
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           article_id
                           TEXT
                           NOT
                           NULL,
                           article_title
                           TEXT,
                           article_url
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ),
                           UNIQUE
                       (
                           user_id,
                           article_id
                       )
                           )
                       ''')

        conn.commit()
        conn.close()

    def create_user(self, username, email, password):
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            password_hash = User.hash_password(password)

            cursor.execute('''
                           INSERT INTO users (username, email, password_hash)
                           VALUES (?, ?, ?)
                           ''', (username, email, password_hash))

            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError as e:
            print(f"Database integrity error: {e}")
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id, username, email, password_hash, created_at, is_active
                           FROM users
                           WHERE id = ?
                           ''', (user_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                # Unpack the row data properly
                id, username, email, password_hash, created_at, is_active = row
                return User(id, username, email, password_hash, created_at, bool(is_active))
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id, username, email, password_hash, created_at, is_active
                           FROM users
                           WHERE username = ?
                           ''', (username,))

            row = cursor.fetchone()
            conn.close()

            if row:
                # Unpack the row data properly
                id, username, email, password_hash, created_at, is_active = row
                return User(id, username, email, password_hash, created_at, bool(is_active))
            return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None

    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT id, username, email, password_hash, created_at, is_active
                           FROM users
                           WHERE email = ?
                           ''', (email,))

            row = cursor.fetchone()
            conn.close()

            if row:
                # Unpack the row data properly
                id, username, email, password_hash, created_at, is_active = row
                return User(id, username, email, password_hash, created_at, bool(is_active))
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            user = self.get_user_by_username(username)
            if user and User.verify_password(password, user.password_hash) and user.is_active:
                return user
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def add_favorite(self, user_id, article_id, article_title, article_url):
        """Add article to user favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           INSERT INTO user_favorites (user_id, article_id, article_title, article_url)
                           VALUES (?, ?, ?, ?)
                           ''', (user_id, article_id, article_title, article_url))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Article already in favorites
            return False
        except Exception as e:
            print(f"Error adding favorite: {e}")
            return False

    def remove_favorite(self, user_id, article_id):
        """Remove article from user favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           DELETE
                           FROM user_favorites
                           WHERE user_id = ?
                             AND article_id = ?
                           ''', (user_id, article_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing favorite: {e}")
            return False

    def get_user_favorites(self, user_id):
        """Get user's favorite articles"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT article_id, article_title, article_url, created_at
                           FROM user_favorites
                           WHERE user_id = ?
                           ORDER BY created_at DESC
                           ''', (user_id,))

            rows = cursor.fetchall()
            conn.close()

            return rows
        except Exception as e:
            print(f"Error getting user favorites: {e}")
            return []

    def is_favorite(self, user_id, article_id):
        """Check if article is in user's favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT COUNT(*)
                           FROM user_favorites
                           WHERE user_id = ?
                             AND article_id = ?
                           ''', (user_id, article_id))

            count = cursor.fetchone()[0]
            conn.close()

            return count > 0
        except Exception as e:
            print(f"Error checking favorite: {e}")
            return False
