#!/usr/bin/env python
"""
Main migration runner script.
Automatically discovers and runs all migration scripts in order.
"""

import os
import sys
import importlib.util
from pathlib import Path

def run_migrations():
    """Discover and run all migration scripts"""
    migrations_dir = Path(__file__).parent
    backend_dir = migrations_dir.parent

    # Add backend to path so we can import models
    sys.path.insert(0, str(backend_dir))

    # Find all migration files
    migration_files = sorted([f for f in migrations_dir.glob('*.py') if f.name.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))])

    if not migration_files:
        print("No migration files found.")
        return True

    print(f"Found {len(migration_files)} migration(s)")
    print("-" * 50)

    for migration_file in migration_files:
        print(f"\nRunning: {migration_file.name}")
        try:
            # Load and execute the migration module
            spec = importlib.util.spec_from_file_location(migration_file.stem, migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # If the module has a migrate function, call it
            if hasattr(module, 'migrate'):
                db_path = backend_dir / 'instance' / 'app.db'
                if db_path.exists():
                    result = module.migrate(str(db_path))
                    if not result:
                        print(f"❌ Migration {migration_file.name} failed")
                        return False
                else:
                    print(f"⚠️  Database not found at {db_path}")
                    print("Skipping this migration")
        except Exception as e:
            print(f"❌ Error running {migration_file.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    print("\n" + "=" * 50)
    print("✅ All migrations completed successfully!")
    return True


if __name__ == '__main__':
    success = run_migrations()
    sys.exit(0 if success else 1)
