
import sqlite3
from pathlib import Path

# Find the main StockWise-AI project folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Database location
DB_PATH = PROJECT_ROOT / "database" / "stockwise.db"


def get_connection():
    """Create a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """Create the products table if it does not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                batch_number TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                expiry_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_product(product_name, batch_number, quantity, expiry_date):
    """Save a new product in the database."""
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO products (
                product_name,
                batch_number,
                quantity,
                expiry_date
            )
            VALUES (?, ?, ?, ?)
        """, (
            product_name,
            batch_number,
            quantity,
            expiry_date
        ))


def get_products():
    """Retrieve all saved products."""
    with get_connection() as connection:
        products = connection.execute("""
            SELECT *
            FROM products
            ORDER BY id DESC
        """).fetchall()

    return [dict(product) for product in products]


def delete_product(product_id):
    """Delete a product using its database ID."""
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )


# Create the database and table when this module is imported
init_db()
