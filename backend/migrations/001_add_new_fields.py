"""
Database migration script to add new fields for clearance, wishlist, and analytics features.
Run this script to update your database schema.
"""

import sqlite3
import sys
from pathlib import Path

def migrate(db_path):
    """Apply database migrations"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist before adding them
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]

        # Add is_clearance column if it doesn't exist
        if 'is_clearance' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN is_clearance BOOLEAN DEFAULT 0")
            print("✓ Added is_clearance column to products table")

        # Add stock_quantity column if it doesn't exist
        if 'stock_quantity' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN stock_quantity INTEGER")
            print("✓ Added stock_quantity column to products table")

        # Add certification column if it doesn't exist
        if 'certification' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN certification VARCHAR(200)")
            print("✓ Added certification column to products table")

        # Check inquiries table
        cursor.execute("PRAGMA table_info(inquiries)")
        inq_columns = [col[1] for col in cursor.fetchall()]

        # Add source column if it doesn't exist
        if 'source' not in inq_columns:
            cursor.execute("ALTER TABLE inquiries ADD COLUMN source VARCHAR(50)")
            print("✓ Added source column to inquiries table")

        # Add customer_level column if it doesn't exist
        if 'customer_level' not in inq_columns:
            cursor.execute("ALTER TABLE inquiries ADD COLUMN customer_level VARCHAR(20)")
            print("✓ Added customer_level column to inquiries table")

        # Create wishlists table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(100) NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        print("✓ Created wishlists table")

        # Create index on session_id for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wishlists_session_id ON wishlists(session_id)")
        print("✓ Created index on wishlists.session_id")

        conn.commit()
        print("\n✅ Database migration completed successfully!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    # Determine database path
    backend_dir = Path(__file__).parent.parent
    db_path = backend_dir / 'instance' / 'app.db'

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        print("Please ensure the application has been initialized first.")
        sys.exit(1)

    print(f"Running migrations on: {db_path}")
    success = migrate(str(db_path))
    sys.exit(0 if success else 1)
