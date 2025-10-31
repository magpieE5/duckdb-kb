#!/usr/bin/env python3
"""
Export DuckDB knowledge base to portable formats

This creates git-friendly exports that can be:
1. Version controlled (unlike binary .duckdb files)
2. Human-readable
3. Used to restore the database if needed

Usage:
    python export.py --format json --output exports/
    python export.py --format sql --output exports/
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import duckdb
import os

DB_PATH = os.getenv('KNOWLEDGE_DB_PATH', 'knowledge.duckdb')


def export_json(db_path: str, output_dir: Path):
    """Export entire database to JSON files"""

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    con = duckdb.connect(db_path, read_only=True)

    # Export knowledge table
    print("Exporting knowledge entries...")
    knowledge = con.execute("""
        SELECT
            id, category, title, tags, content, metadata,
            embedding IS NOT NULL as has_embedding,
            created, updated
        FROM knowledge
        ORDER BY id
    """).fetchall()

    columns = [desc[0] for desc in con.description]
    knowledge_data = []

    for row in knowledge:
        entry = dict(zip(columns, row))
        # Convert datetime to ISO format
        if entry.get('created'):
            entry['created'] = entry['created'].isoformat()
        if entry.get('updated'):
            entry['updated'] = entry['updated'].isoformat()
        knowledge_data.append(entry)

    knowledge_file = output_dir / f"knowledge_{timestamp}.json"
    with open(knowledge_file, 'w') as f:
        json.dump(knowledge_data, f, indent=2, default=str)

    print(f"✅ Exported {len(knowledge_data)} entries to {knowledge_file}")

    # Export links
    print("Exporting links...")
    links = con.execute("SELECT * FROM knowledge_links ORDER BY from_id").fetchall()
    links_columns = [desc[0] for desc in con.description]
    links_data = [dict(zip(links_columns, row)) for row in links]

    if links_data:
        links_file = output_dir / f"links_{timestamp}.json"
        with open(links_file, 'w') as f:
            json.dump(links_data, f, indent=2)
        print(f"✅ Exported {len(links_data)} links to {links_file}")

    # Export stats
    stats = con.execute("SELECT * FROM knowledge_stats").fetchone()
    stats_data = dict(zip([desc[0] for desc in con.description], stats))

    stats_file = output_dir / f"stats_{timestamp}.json"
    with open(stats_file, 'w') as f:
        json.dump(stats_data, f, indent=2, default=str)

    print(f"✅ Exported stats to {stats_file}")

    # Create latest symlink (without timestamp for easy git tracking)
    latest_knowledge = output_dir / "knowledge_latest.json"
    if latest_knowledge.exists():
        latest_knowledge.unlink()
    latest_knowledge.symlink_to(knowledge_file.name)

    latest_links = output_dir / "links_latest.json"
    if latest_links.exists():
        latest_links.unlink()
    if links_data:
        latest_links.symlink_to(links_file.name)

    con.close()

    return {
        'knowledge_file': knowledge_file,
        'links_file': links_file if links_data else None,
        'stats_file': stats_file,
        'entry_count': len(knowledge_data),
        'link_count': len(links_data)
    }


def export_sql(db_path: str, output_dir: Path):
    """Export database as SQL INSERT statements"""

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    con = duckdb.connect(db_path, read_only=True)

    sql_file = output_dir / f"knowledge_{timestamp}.sql"

    with open(sql_file, 'w') as f:
        # Write header
        f.write("-- DuckDB Knowledge Base Export\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write("-- WARNING: This file does NOT include embeddings (too large)\n")
        f.write("-- Run generate_embeddings.py after importing\n\n")

        # Export knowledge (without embeddings)
        f.write("-- Knowledge entries\n")
        entries = con.execute("""
            SELECT id, category, title, tags, content, metadata, created, updated
            FROM knowledge
            ORDER BY id
        """).fetchall()

        for entry in entries:
            id, category, title, tags, content, metadata, created, updated = entry

            # Escape single quotes
            content_escaped = content.replace("'", "''") if content else ''
            title_escaped = title.replace("'", "''") if title else ''

            f.write(f"""
INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
VALUES (
    '{id}',
    '{category}',
    '{title_escaped}',
    {tags},
    '{content_escaped}',
    '{metadata}'::JSON,
    '{created}'::TIMESTAMP,
    '{updated}'::TIMESTAMP
);
""")

        # Export links
        f.write("\n-- Knowledge links\n")
        links = con.execute("SELECT * FROM knowledge_links").fetchall()
        for link in links:
            from_id, to_id, link_type = link
            f.write(f"INSERT INTO knowledge_links VALUES ('{from_id}', '{to_id}', '{link_type}');\n")

    con.close()

    print(f"✅ Exported to {sql_file}")
    print(f"   Entries: {len(entries)}")
    print(f"   Links: {len(links)}")
    print(f"   ⚠️  Embeddings NOT included (regenerate after import)")

    return sql_file


def main():
    parser = argparse.ArgumentParser(description='Export DuckDB knowledge base')
    parser.add_argument('--format', choices=['json', 'sql', 'both'], default='json',
                      help='Export format (default: json)')
    parser.add_argument('--output', type=Path, default='exports',
                      help='Output directory (default: exports/)')
    parser.add_argument('--db-path', type=str, default=DB_PATH,
                      help=f'Database path (default: {DB_PATH})')

    args = parser.parse_args()

    if not Path(args.db_path).exists():
        print(f"❌ Database not found: {args.db_path}")
        return 1

    print(f"Exporting from: {args.db_path}")
    print(f"Output directory: {args.output}")
    print()

    if args.format in ['json', 'both']:
        result = export_json(args.db_path, args.output)
        print()
        print("JSON Export Summary:")
        print(f"  Knowledge: {result['entry_count']} entries")
        print(f"  Links: {result['link_count']} links")
        print(f"  Latest: {args.output}/knowledge_latest.json")

    if args.format in ['sql', 'both']:
        print()
        sql_file = export_sql(args.db_path, args.output)
        print(f"  SQL file: {sql_file}")

    print()
    print("✅ Export complete!")
    print()
    print("💡 Tip: Add exports/ to git for version-controlled backups:")
    print("   git add exports/knowledge_latest.json exports/links_latest.json")
    print("   git commit -m 'Backup knowledge base'")

    return 0


if __name__ == '__main__':
    exit(main())
