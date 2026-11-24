#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database migration script to add missing columns to products table
"""
import os
import sys
from sqlalchemy import text

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db

def migrate():
    """Run database migrations"""
    app = create_app()

    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()

            # Check if columns exist and add them if they don't
            migrations = [
                ("products", "is_clearance", "ALTER TABLE products ADD COLUMN is_clearance BOOLEAN DEFAULT FALSE"),
                ("products", "certification", "ALTER TABLE products ADD COLUMN certification VARCHAR(200)"),
                ("products", "stock_quantity", "ALTER TABLE products ADD COLUMN stock_quantity INT"),
                ("products", "view_count", "ALTER TABLE products ADD COLUMN view_count INT DEFAULT 0"),
                ("inquiries", "source", "ALTER TABLE inquiries ADD COLUMN source VARCHAR(50)"),
                ("inquiries", "customer_level", "ALTER TABLE inquiries ADD COLUMN customer_level VARCHAR(20)"),
                ("inquiries", "admin_reply", "ALTER TABLE inquiries ADD COLUMN admin_reply TEXT"),
                ("inquiries", "user_id", "ALTER TABLE inquiries ADD COLUMN user_id INT, ADD CONSTRAINT fk_inquiry_user FOREIGN KEY (user_id) REFERENCES users(id)"),
                ("users", "email", "ALTER TABLE users ADD COLUMN email VARCHAR(120)"),
                ("users", "company_name", "ALTER TABLE users ADD COLUMN company_name VARCHAR(200)"),
                ("users", "country", "ALTER TABLE users ADD COLUMN country VARCHAR(100)"),
                ("users", "phone", "ALTER TABLE users ADD COLUMN phone VARCHAR(50)"),
                ("wishlists", "user_id", "ALTER TABLE wishlists ADD COLUMN user_id INT, ADD CONSTRAINT fk_wishlist_user FOREIGN KEY (user_id) REFERENCES users(id)"),
                ("products", "clearance_type", "ALTER TABLE products ADD COLUMN clearance_type VARCHAR(50)"),
                ("messages", "msg_type", "ALTER TABLE messages ADD COLUMN msg_type VARCHAR(10) NOT NULL DEFAULT 'text'"),
                ("messages", "quote_price", "ALTER TABLE messages ADD COLUMN quote_price DECIMAL(10,2) NULL"),
                ("messages", "quote_status", "ALTER TABLE messages ADD COLUMN quote_status VARCHAR(10) NULL"),
                ("users", "source", "ALTER TABLE users ADD COLUMN source VARCHAR(50)"),
                ("factories", "certification_files", "ALTER TABLE factories ADD COLUMN certification_files TEXT"),
                ("products", "is_banner", "ALTER TABLE products ADD COLUMN is_banner BOOLEAN DEFAULT FALSE"),
                ("products", "poster_images", "ALTER TABLE products ADD COLUMN poster_images TEXT"),
            ]

            # Also make session_id nullable for wishlists (was NOT NULL)
            special_column_migrations = [
                "ALTER TABLE wishlists MODIFY COLUMN session_id VARCHAR(100) NULL",
            ]

            for table_name, col_name, sql in migrations:
                try:
                    # Check if column exists
                    check_sql = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}' AND COLUMN_NAME='{col_name}'"
                    cursor.execute(check_sql)
                    if not cursor.fetchone():
                        print(f"Adding column: {col_name}")
                        cursor.execute(sql)
                        connection.commit()
                        print(f"[OK] Column {col_name} added successfully")
                    else:
                        print(f"[OK] Column {col_name} already exists")
                except Exception as e:
                    print(f"[ERROR] Error adding column {col_name}: {e}")
                    connection.rollback()

            cursor.close()

            # Run special column modifications
            cursor_sp = connection.cursor()
            for sql in special_column_migrations:
                try:
                    cursor_sp.execute(sql)
                    connection.commit()
                    print(f"[OK] {sql[:60]}...")
                except Exception as e:
                    print(f"[INFO] {e}")
                    connection.rollback()
            cursor_sp.close()

            # Special migrations: role enum update + messages table
            cursor2 = connection.cursor()
            try:
                cursor2.execute("ALTER TABLE users MODIFY COLUMN role ENUM('admin','factory','buyer') NOT NULL DEFAULT 'factory'")
                connection.commit()
                print("[OK] User role enum updated to include 'buyer'")
            except Exception as e:
                if 'Duplicate' not in str(e):
                    print(f"[INFO] Role enum update: {e}")
                connection.rollback()

            try:
                cursor2.execute("""CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    inquiry_id INT NOT NULL,
                    sender_id INT NOT NULL,
                    content TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (inquiry_id) REFERENCES inquiries(id),
                    FOREIGN KEY (sender_id) REFERENCES users(id),
                    INDEX idx_msg_inquiry (inquiry_id),
                    INDEX idx_msg_sender (sender_id)
                )""")
                connection.commit()
                print("[OK] Messages table created/verified")
            except Exception as e:
                print(f"[INFO] Messages table: {e}")
                connection.rollback()

            try:
                cursor2.execute("""CREATE TABLE IF NOT EXISTS site_settings (
                    `key` VARCHAR(200) PRIMARY KEY,
                    `value` TEXT DEFAULT ''
                )""")
                connection.commit()
                print("[OK] Site settings table created/verified")
            except Exception as e:
                print(f"[INFO] Site settings table: {e}")
                connection.rollback()

            cursor2.close()
            connection.close()
            print("\n[OK] Migration completed successfully!")

        except Exception as e:
            print(f"[ERROR] Migration failed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    migrate()
