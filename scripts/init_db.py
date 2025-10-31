#!/usr/bin/env python3
"""
Initialize DuckDB Knowledge Base

This script sets up a new knowledge base database with:
- Schema (tables, indexes, views)
- Functions/Macros for MCP server
- Optional: VSS extension for semantic search

Usage:
    python scripts/init_db.py                    # Initialize default database
    python scripts/init_db.py --db custom.duckdb # Initialize custom database
    python scripts/init_db.py --validate         # Validate existing database
"""

import argparse
import os
import sys
from pathlib import Path
import duckdb

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = PROJECT_ROOT / 'schema.sql'
FUNCTIONS_PATH = PROJECT_ROOT / 'add_functions.sql'
DEFAULT_DB_PATH = PROJECT_ROOT / 'knowledge.duckdb'


def print_status(symbol, message):
    """Print colored status message"""
    colors = {
        '✅': '\033[92m',  # Green
        '⚠️': '\033[93m',   # Yellow
        '❌': '\033[91m',  # Red
        'ℹ️': '\033[94m',   # Blue
    }
    reset = '\033[0m'
    color = colors.get(symbol, '')
    print(f"{color}{symbol} {message}{reset}")


def execute_sql_file(con, file_path, skip_macros=False):
    """Execute SQL file, optionally skipping problematic MACRO definitions"""
    with open(file_path) as f:
        content = f.read()

    if skip_macros:
        # Split into statements, skip MACRO definitions
        lines = []
        in_macro = False
        paren_depth = 0

        for line in content.split('\n'):
            stripped = line.strip()

            # Skip comments
            if stripped.startswith('--') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            # Detect MACRO definitions (they have issues with MERGE)
            if 'CREATE MACRO' in line and 'upsert_knowledge' in line:
                in_macro = True
                continue

            if in_macro:
                if '(' in line:
                    paren_depth += line.count('(')
                if ')' in line:
                    paren_depth -= line.count(')')
                if paren_depth == 0 and ');' in line:
                    in_macro = False
                continue

            lines.append(line)

        content = '\n'.join(lines)

    # Execute statements one by one
    statements = [s.strip() for s in content.split(';') if s.strip()]

    for stmt in statements:
        if not stmt or stmt.startswith('--') or stmt.startswith('/*'):
            continue

        try:
            con.execute(stmt + ';')
        except Exception as e:
            # Ignore "already exists" errors
            if 'already exists' in str(e):
                continue
            # Ignore test SELECT statements
            if stmt.strip().upper().startswith('SELECT'):
                continue
            raise Exception(f"Error executing statement: {stmt[:100]}...\nError: {e}")


def check_vss_extension(con):
    """Check if VSS extension is available"""
    try:
        con.execute("INSTALL vss")
        con.execute("LOAD vss")
        return True
    except Exception as e:
        return False


def validate_database(db_path):
    """Validate that database is properly initialized"""
    print_status('ℹ️', f'Validating database: {db_path}')

    if not os.path.exists(db_path):
        print_status('❌', f'Database file does not exist: {db_path}')
        return False

    con = duckdb.connect(str(db_path))

    try:
        # Check tables exist
        tables = con.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]

        required_tables = ['knowledge', 'knowledge_links']
        for table in required_tables:
            if table in table_names:
                print_status('✅', f'Table "{table}" exists')
            else:
                print_status('❌', f'Table "{table}" missing')
                return False

        # Check functions exist
        try:
            result = con.execute("SELECT * FROM database_summary()").fetchall()
            print_status('✅', 'Function "database_summary()" exists')

            # Print database stats
            print('\n📊 Database Statistics:')
            for metric, value in result:
                print(f'   {metric}: {value}')
        except Exception as e:
            print_status('❌', f'Function "database_summary()" missing or broken: {e}')
            return False

        # Check VSS extension
        if check_vss_extension(con):
            print_status('✅', 'VSS extension available (semantic search enabled)')
        else:
            print_status('⚠️', 'VSS extension not available (semantic search disabled)')

        print_status('✅', 'Database validation PASSED')
        return True

    except Exception as e:
        print_status('❌', f'Validation failed: {e}')
        return False
    finally:
        con.close()


def initialize_database(db_path, force=False):
    """Initialize a new database with schema and functions"""
    print_status('ℹ️', f'Initializing database: {db_path}')

    # Check if database already exists
    if os.path.exists(db_path) and not force:
        print_status('⚠️', f'Database already exists: {db_path}')
        print('         Use --force to reinitialize, or --validate to check status')
        return False

    # Create database connection
    con = duckdb.connect(str(db_path))

    try:
        # 1. Install VSS extension
        print_status('ℹ️', 'Installing VSS extension...')
        has_vss = check_vss_extension(con)
        if has_vss:
            print_status('✅', 'VSS extension loaded')
        else:
            print_status('⚠️', 'VSS extension not available (semantic search will be disabled)')

        # 2. Create schema
        print_status('ℹ️', 'Creating schema (tables, indexes, views)...')
        execute_sql_file(con, SCHEMA_PATH, skip_macros=True)
        print_status('✅', 'Schema created')

        # 3. Add functions
        print_status('ℹ️', 'Adding helper functions and macros...')
        execute_sql_file(con, FUNCTIONS_PATH, skip_macros=False)
        print_status('✅', 'Functions added')

        # 4. Validate
        con.close()
        print()
        if validate_database(db_path):
            print()
            print_status('✅', 'Database initialization COMPLETE!')
            print()
            print('Next steps:')
            print('  1. Configure MCP server environment variable:')
            print(f'     export KNOWLEDGE_DB_PATH="{db_path}"')
            print('  2. Start the MCP server:')
            print('     python mcp_server.py')
            print('  3. Add your first entry using the MCP tools!')
            return True
        else:
            print_status('❌', 'Initialization completed but validation failed')
            return False

    except Exception as e:
        print_status('❌', f'Initialization failed: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Initialize or validate DuckDB Knowledge Base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/init_db.py                    # Initialize default database
  python scripts/init_db.py --validate         # Validate existing database
  python scripts/init_db.py --db custom.duckdb # Initialize custom database
  python scripts/init_db.py --force            # Reinitialize existing database
        """
    )

    parser.add_argument(
        '--db',
        default=DEFAULT_DB_PATH,
        help=f'Database path (default: {DEFAULT_DB_PATH})'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing database instead of initializing'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reinitialize even if database exists'
    )

    args = parser.parse_args()

    # Convert to Path object
    db_path = Path(args.db).resolve()

    print()
    print('=' * 70)
    print('  DuckDB Knowledge Base Setup')
    print('=' * 70)
    print()

    if args.validate:
        success = validate_database(db_path)
    else:
        success = initialize_database(db_path, force=args.force)

    print()
    print('=' * 70)
    print()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
