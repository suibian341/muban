# Database Migrations

This directory contains database migration scripts for the Chenghai B2B platform.

## Running Migrations

### For SQLite (Development)

```bash
cd backend
python migrations/001_add_new_fields.py
```

### For PostgreSQL/MySQL (Production)

If you're using Flask-Migrate with Alembic:

```bash
cd backend
flask db upgrade
```

## Migration Scripts

### 001_add_new_fields.py
Adds new fields and tables for:
- **Products table**: `is_clearance`, `stock_quantity`, `certification`
- **Inquiries table**: `source`, `customer_level`
- **Wishlists table**: New table for wishlist functionality

## Creating New Migrations

To create a new migration:

1. Create a new Python file in this directory with the naming convention: `NNN_description.py`
2. Implement the migration logic in the file
3. Run the migration script

## Rollback

Currently, rollback is not supported. If you need to rollback, you'll need to:
1. Restore from a database backup
2. Or manually revert the changes using SQL

## Notes

- Always backup your database before running migrations
- Test migrations on a development database first
- Migrations are idempotent (safe to run multiple times)
