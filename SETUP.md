# Database Setup Guide

This guide explains how to set up and migrate the database for the Chenghai B2B platform.

## Initial Setup

### 1. Create Database Instance

```bash
cd backend
mkdir -p instance
```

### 2. Initialize Database with Flask

```bash
# Set Flask app
export FLASK_APP=app.py  # On Windows: set FLASK_APP=app.py

# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 3. Run Migrations

After creating the initial database, run migrations to add new fields:

```bash
python migrations/run.py
```

Or run individual migrations:

```bash
python migrations/001_add_new_fields.py
```

## Database Schema

### Tables

- **users**: User accounts (admin, factory)
- **factories**: Factory information
- **products**: Product listings
- **categories**: Product categories
- **inquiries**: Customer inquiries
- **wishlists**: Customer wishlists (new)

### New Fields Added by Migrations

#### Products Table
- `is_clearance` (BOOLEAN): Mark product as clearance/closeout
- `stock_quantity` (INTEGER): Available stock quantity
- `certification` (VARCHAR): Product certifications (CE, FCC, etc.)

#### Inquiries Table
- `source` (VARCHAR): Source of inquiry (website, wishlist, etc.)
- `customer_level` (VARCHAR): Customer tier (new, regular, vip)

#### Wishlists Table (New)
- `id` (INTEGER): Primary key
- `session_id` (VARCHAR): Session identifier
- `product_id` (INTEGER): Foreign key to products
- `quantity` (INTEGER): Quantity in wishlist
- `created_at` (DATETIME): Creation timestamp

## Verification

To verify the database setup:

```bash
# Check database file exists
ls -la instance/app.db

# Check tables (SQLite)
sqlite3 instance/app.db ".tables"

# Check schema
sqlite3 instance/app.db ".schema products"
```

## Troubleshooting

### Database file not found
- Ensure you've run the initial setup steps
- Check that the `instance` directory exists

### Migration fails
- Backup your database first
- Check that the database file is not locked
- Review the error message for specific issues

### Columns already exist
- Migrations are idempotent and will skip existing columns
- This is safe to run multiple times

## Production Deployment

For production, consider using:
- PostgreSQL or MySQL instead of SQLite
- Flask-Migrate with Alembic for version control
- Automated backup before migrations
- Staging environment testing

See `migrations/README.md` for more details.
