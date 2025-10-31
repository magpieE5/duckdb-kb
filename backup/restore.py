#!/usr/bin/env python3
"""
Restore DuckDB knowledge base from exports

This can restore from:
1. JSON exports (created by export.py) - RECOMMENDED
2. SQL dumps

Usage:
    python restore.py --from-json exports/knowledge_latest.json
    python restore.py --from-sql exports/knowledge_20250130_120000.sql

Note: JSON format is recommended as it's human-readable and can be reviewed/edited before restore.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import duckdb
import os

DB_PATH = os.getenv('KNOWLEDGE_DB_PATH', 'knowledge.duckdb')


def restore_from_json(json_file: Path, db_path: str):
    """Restore database from JSON export"""

    print(f"Restoring from JSON: {json_file}")

    with open(json_file, 'r') as f:
        entries = json.load(f)

    print(f"Found {len(entries)} entries")

    # Create/connect to database
    con = duckdb.connect(db_path)

    # Create basic tables (don't load full schema.sql - it has macros/functions)
    print("Creating tables...")
    con.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id VARCHAR PRIMARY KEY,
            category VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            tags VARCHAR[],
            content TEXT,
            metadata JSON,
            embedding FLOAT[1536],
            created TIMESTAMP,
            updated TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS knowledge_links (
            from_id VARCHAR,
            to_id VARCHAR,
            link_type VARCHAR DEFAULT 'related',
            PRIMARY KEY (from_id, to_id)
        );
    """)

    # Insert entries
    print("Inserting entries...")
    for i, entry in enumerate(entries, 1):
        if i % 10 == 0:
            print(f"  {i}/{len(entries)}...", end='\r')

        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
            VALUES (?, ?, ?, ?, ?, ?::JSON, ?::TIMESTAMP, ?::TIMESTAMP)
        """, [
            entry['id'],
            entry['category'],
            entry['title'],
            entry['tags'],
            entry['content'],
            entry.get('metadata', '{}'),
            entry['created'],
            entry['updated']
        ])

    print(f"  {len(entries)}/{len(entries)}... Done!")

    # Restore links if available
    links_file = json_file.parent / json_file.name.replace('knowledge', 'links')
    if links_file.exists():
        print(f"Restoring links from {links_file}")
        with open(links_file, 'r') as f:
            links = json.load(f)

        for link in links:
            con.execute("""
                INSERT INTO knowledge_links (from_id, to_id, link_type)
                VALUES (?, ?, ?)
            """, [link['from_id'], link['to_id'], link['link_type']])

        print(f"✅ Restored {len(links)} links")

    con.close()

    print(f"✅ Restored {len(entries)} entries")
    print()
    print("⚠️  Embeddings were NOT restored (they're too large for JSON)")
    print("   Run: python generate_embeddings.py")

    return len(entries)


def restore_from_sql(sql_file: Path, db_path: str):
    """Restore database from SQL dump"""

    print(f"Restoring from SQL: {sql_file}")

    # Create/connect to database
    con = duckdb.connect(db_path)

    # Create basic tables (don't load full schema.sql - it has macros/functions)
    print("Creating tables...")
    con.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id VARCHAR PRIMARY KEY,
            category VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            tags VARCHAR[],
            content TEXT,
            metadata JSON,
            embedding FLOAT[1536],
            created TIMESTAMP,
            updated TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS knowledge_links (
            from_id VARCHAR,
            to_id VARCHAR,
            link_type VARCHAR DEFAULT 'related',
            PRIMARY KEY (from_id, to_id)
        );
    """)

    # Execute SQL dump
    print("Executing SQL dump...")
    sql_content = sql_file.read_text()
    con.execute(sql_content)

    # Get count
    count = con.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    link_count = con.execute("SELECT COUNT(*) FROM knowledge_links").fetchone()[0]

    con.close()

    print(f"✅ Restored {count} entries and {link_count} links")
    print()
    print("⚠️  Embeddings were NOT restored")
    print("   Run: python generate_embeddings.py")

    return count


def main():
    parser = argparse.ArgumentParser(description='Restore DuckDB knowledge base from JSON/SQL exports')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--from-json', type=Path, help='Restore from JSON export (recommended)')
    group.add_argument('--from-sql', type=Path, help='Restore from SQL dump')

    parser.add_argument('--db-path', type=str, default=DB_PATH,
                      help=f'Target database path (default: {DB_PATH})')
    parser.add_argument('--force', action='store_true',
                      help='Overwrite existing database without confirmation')

    args = parser.parse_args()

    # Check if target database exists
    if Path(args.db_path).exists() and not args.force:
        response = input(f"⚠️  Database exists: {args.db_path}\n   Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return 1

        # Remove existing database
        Path(args.db_path).unlink()
        print(f"Removed: {args.db_path}")

    # Perform restore
    try:
        if args.from_json:
            if not args.from_json.exists():
                print(f"❌ JSON file not found: {args.from_json}")
                return 1
            restore_from_json(args.from_json, args.db_path)

        elif args.from_sql:
            if not args.from_sql.exists():
                print(f"❌ SQL file not found: {args.from_sql}")
                return 1
            restore_from_sql(args.from_sql, args.db_path)

        print()
        print(f"✅ Restore complete: {args.db_path}")

    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
