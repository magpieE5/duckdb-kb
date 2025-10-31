#!/usr/bin/env python3
"""
Generate embeddings for all knowledge entries using OpenAI

This script generates embeddings for entries that don't have them yet.
"""

import os
import duckdb
from openai import OpenAI

# Configuration
DB_PATH = 'knowledge.duckdb'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = 'text-embedding-3-small'
BATCH_SIZE = 100  # OpenAI supports large batches

def main():
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set")
        print("Run: export OPENAI_API_KEY='sk-...'")
        return 1

    # Connect to database
    con = duckdb.connect(DB_PATH)
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Find entries without embeddings
    result = con.execute("""
        SELECT id, title, tags, content
        FROM knowledge
        WHERE embedding IS NULL
    """).fetchall()

    if not result:
        print("✓ All entries already have embeddings!")
        return 0

    print(f"Generating embeddings for {len(result)} entries...")
    print(f"Using OpenAI {EMBEDDING_MODEL}")
    print()

    # Prepare texts for embedding
    entries = []
    texts = []
    for row in result:
        entry_id, title, tags, content = row
        # Create rich embedding text
        embed_text = f"Title: {title}\nTags: {', '.join(tags)}\nContent: {content}"
        entries.append(entry_id)
        texts.append(embed_text)

    # Generate embeddings in batches
    total_updated = 0
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_ids = entries[i:i+BATCH_SIZE]

        print(f"Processing batch {i//BATCH_SIZE + 1}/{(len(texts)-1)//BATCH_SIZE + 1} ({len(batch_texts)} entries)...")

        # Call OpenAI API
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch_texts
        )

        # Update database
        for entry_id, embedding_data in zip(batch_ids, response.data):
            embedding = embedding_data.embedding
            con.execute(
                "UPDATE knowledge SET embedding = ?, updated = CURRENT_TIMESTAMP WHERE id = ?",
                [embedding, entry_id]
            )
            total_updated += 1
            print(f"  ✓ {entry_id}")

    print()
    print(f"✓ Generated {total_updated} embeddings successfully!")
    print(f"Model: {EMBEDDING_MODEL} (1536 dimensions)")

    # Show stats
    stats = con.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(embedding) as with_embeddings,
            (COUNT(embedding)::FLOAT / COUNT(*)::FLOAT * 100)::INTEGER as pct
        FROM knowledge
    """).fetchone()

    print()
    print("="*60)
    print("EMBEDDING STATUS")
    print("="*60)
    print(f"Total entries:      {stats[0]}")
    print(f"With embeddings:    {stats[1]}")
    print(f"Coverage:           {stats[2]}%")
    print()

    con.close()
    return 0


if __name__ == '__main__':
    exit(main())
