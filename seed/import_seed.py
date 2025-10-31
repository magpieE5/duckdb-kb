#!/usr/bin/env python3
"""
Import seed data into DuckDB knowledge base

Usage:
    python import_seed.py
    python import_seed.py --seed-file custom_seed.json
    python import_seed.py --db-path /path/to/knowledge.duckdb
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import mcp_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import duckdb


def import_seed_data(seed_file: str, db_path: str):
    """
    Import seed data from JSON file into knowledge base

    Args:
        seed_file: Path to seed.json file
        db_path: Path to DuckDB database
    """
    print(f"Importing seed data from: {seed_file}")
    print(f"Target database: {db_path}")

    # Load seed data
    with open(seed_file, 'r') as f:
        entries = json.load(f)

    print(f"Found {len(entries)} entries to import")

    # Connect to database
    con = duckdb.connect(db_path)

    # Check if knowledge table exists
    tables = con.execute("SHOW TABLES").fetchall()
    if not any('knowledge' in str(t) for t in tables):
        print("ERROR: knowledge table not found!")
        print("Please run schema.sql first:")
        print(f"  duckdb {db_path} < schema.sql")
        return False

    # Import each entry
    imported = 0
    skipped = 0
    updated = 0

    for entry in entries:
        entry_id = entry['id']

        # Check if entry already exists
        existing = con.execute(
            "SELECT id FROM knowledge WHERE id = ?",
            [entry_id]
        ).fetchone()

        if existing:
            # Ask user whether to update
            response = input(f"Entry '{entry_id}' already exists. Update? (y/n): ")
            if response.lower() != 'y':
                print(f"  Skipped: {entry_id}")
                skipped += 1
                continue

            # Update existing entry
            con.execute("""
                UPDATE knowledge
                SET category = ?,
                    title = ?,
                    tags = ?,
                    content = ?,
                    metadata = ?,
                    updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, [
                entry['category'],
                entry['title'],
                entry['tags'],
                entry['content'],
                json.dumps(entry.get('metadata', {})),
                entry_id
            ])
            print(f"  Updated: {entry_id}")
            updated += 1
        else:
            # Insert new entry
            con.execute("""
                INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, [
                entry_id,
                entry['category'],
                entry['title'],
                entry['tags'],
                entry['content'],
                json.dumps(entry.get('metadata', {}))
            ])
            print(f"  Imported: {entry_id}")
            imported += 1

    # Summary
    print(f"\n✅ Import complete!")
    print(f"  Imported: {imported}")
    print(f"  Updated: {updated}")
    print(f"  Skipped: {skipped}")
    print(f"  Total: {imported + updated + skipped}")

    # Check embedding status
    no_embeddings = con.execute("""
        SELECT COUNT(*) FROM knowledge WHERE embedding IS NULL
    """).fetchone()[0]

    if no_embeddings > 0:
        print(f"\n⚠️  {no_embeddings} entries have no embeddings")
        print("Generate embeddings with:")
        print("  python generate_embeddings.py")
        print("Or via MCP tool:")
        print("  mcp__duckdb-knowledge__generate_embeddings({})")

    con.close()
    return True


def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Import seed data into knowledge base')
    parser.add_argument(
        '--seed-file',
        default=str(Path(__file__).parent / 'seed.json'),
        help='Path to seed.json file (default: seed/seed.json)'
    )
    parser.add_argument(
        '--db-path',
        default=str(Path(__file__).parent.parent / 'knowledge.duckdb'),
        help='Path to DuckDB database (default: ../knowledge.duckdb)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Update existing entries without asking'
    )

    args = parser.parse_args()

    # Check files exist
    if not Path(args.seed_file).exists():
        print(f"ERROR: Seed file not found: {args.seed_file}")
        return 1

    if not Path(args.db_path).exists():
        print(f"ERROR: Database not found: {args.db_path}")
        print("Create database with:")
        print(f"  duckdb {args.db_path} < schema.sql")
        return 1

    # Import
    success = import_seed_data(args.seed_file, args.db_path)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
