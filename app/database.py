import sqlite3
from transaction import Transaction
from user import User

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('finance_tracker.db')
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                description TEXT,
                type TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()

    def add_transaction(self, transaction, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (amount, category, description, type, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (transaction.amount, transaction.category, transaction.description, transaction.type, user_id))
        self.conn.commit()    

    def get_all_transactions(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            # Create a Transaction object with amount, category, description, type, date
            transaction = Transaction(row[1], row[2], row[3], row[4], row[5])
            transactions.append(transaction)
        return transactions

    def clear_transactions(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
        self.conn.commit()
        print("All transactions have been deleted.")

    def add_user(self, username, password, email=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', (username, password, email))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username or email already exists

    def get_user_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        return User.from_db_row(user_row) if user_row else None

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user_row = cursor.fetchone()
        return User.from_db_row(user_row) if user_row else None

    def __del__(self):
        self.conn.close()
