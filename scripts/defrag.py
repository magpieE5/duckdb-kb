#!/usr/bin/env python3
"""
Knowledge Base Defragmentation Tool

Detects and helps resolve:
1. Duplicate entries (high similarity)
2. Conflicting information
3. Fragmented topics (should be consolidated)
4. Orphaned entries (no tags, no links)
5. Obsolete entries (old, unused)

Usage:
    python scripts/defrag.py --check          # Run all checks
    python scripts/defrag.py --duplicates     # Find duplicates only
    python scripts/defrag.py --conflicts      # Find conflicts only
    python scripts/defrag.py --fragmentation  # Find fragmentation only
    python scripts/defrag.py --orphans        # Find orphans only
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import duckdb


# Thresholds
DUPLICATE_THRESHOLD = 0.92      # Likely exact duplicate
CONFLICT_THRESHOLD = 0.75       # Possibly related, check for conflicts
FRAGMENTATION_COUNT = 3         # 3+ entries on same topic = fragmented
ORPHAN_TAG_COUNT = 0            # Entries with no tags
OBSOLETE_DAYS = 365             # Not updated in 1 year


class DefragAnalyzer:
    """Analyze knowledge base for fragmentation issues"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.con = duckdb.connect(db_path, read_only=True)

        # Check if embeddings exist
        self._check_embeddings()

    def _check_embeddings(self):
        """Check if embeddings are available for analysis"""
        result = self.con.execute("""
            SELECT COUNT(*) as total,
                   COUNT(embedding) as with_embeddings
            FROM knowledge
        """).fetchone()

        total, with_embeddings = result

        if with_embeddings == 0:
            print("⚠️  WARNING: No embeddings found!")
            print("Semantic similarity checks will not work.")
            print("Generate embeddings with: python generate_embeddings.py")
            self.has_embeddings = False
        elif with_embeddings < total:
            print(f"⚠️  WARNING: Only {with_embeddings}/{total} entries have embeddings")
            print("Some entries may be missed in similarity checks.")
            self.has_embeddings = True
        else:
            self.has_embeddings = True

    def find_duplicates(self, threshold: float = DUPLICATE_THRESHOLD) -> List[Tuple]:
        """
        Find likely duplicate entries (similarity > threshold)

        Returns list of (id1, id2, similarity, title1, title2)
        """
        if not self.has_embeddings:
            print("Cannot find duplicates without embeddings")
            return []

        print(f"\n🔍 Finding duplicates (similarity > {threshold})...")

        # Find pairs with high similarity
        duplicates = self.con.execute(f"""
            WITH pairs AS (
                SELECT
                    a.id as id1,
                    a.title as title1,
                    b.id as id2,
                    b.title as title2,
                    array_cosine_similarity(a.embedding, b.embedding) as similarity
                FROM knowledge a
                CROSS JOIN knowledge b
                WHERE a.id < b.id  -- Avoid duplicates and self-comparison
                  AND a.embedding IS NOT NULL
                  AND b.embedding IS NOT NULL
            )
            SELECT id1, id2, similarity, title1, title2
            FROM pairs
            WHERE similarity > {threshold}
            ORDER BY similarity DESC
        """).fetchall()

        if duplicates:
            print(f"Found {len(duplicates)} potential duplicates:\n")
            for id1, id2, sim, title1, title2 in duplicates:
                print(f"  {sim:.3f} | {id1} ↔ {id2}")
                print(f"         | {title1}")
                print(f"         | {title2}")
                print()

        return duplicates

    def find_conflicts(self, threshold: float = CONFLICT_THRESHOLD) -> List[Dict]:
        """
        Find entries with moderate similarity that might contain
        conflicting information. Requires human review.

        Returns list of similar entry groups for manual review
        """
        if not self.has_embeddings:
            print("Cannot find conflicts without embeddings")
            return []

        print(f"\n🔍 Finding potential conflicts (similarity {threshold}-{DUPLICATE_THRESHOLD})...")

        # Find similar entries that might conflict
        similar_pairs = self.con.execute(f"""
            WITH pairs AS (
                SELECT
                    a.id as id1,
                    a.title as title1,
                    a.category as cat1,
                    a.content as content1,
                    b.id as id2,
                    b.title as title2,
                    b.category as cat2,
                    b.content as content2,
                    array_cosine_similarity(a.embedding, b.embedding) as similarity
                FROM knowledge a
                CROSS JOIN knowledge b
                WHERE a.id < b.id
                  AND a.embedding IS NOT NULL
                  AND b.embedding IS NOT NULL
            )
            SELECT *
            FROM pairs
            WHERE similarity > {threshold}
              AND similarity <= {DUPLICATE_THRESHOLD}
              AND (cat1 = cat2 OR cat1 IN ('pattern', 'troubleshooting') AND cat2 IN ('pattern', 'troubleshooting'))
            ORDER BY similarity DESC
        """).fetchall()

        if similar_pairs:
            print(f"Found {len(similar_pairs)} pairs that should be reviewed for conflicts:\n")

            conflicts = []
            for row in similar_pairs:
                id1, title1, cat1, content1, id2, title2, cat2, content2, sim = row

                print(f"  {sim:.3f} | {id1} ↔ {id2}")
                print(f"         | [{cat1}] {title1}")
                print(f"         | [{cat2}] {title2}")

                # Simple heuristic: Look for conflicting words
                conflict_indicators = self._detect_conflict_indicators(content1, content2)
                if conflict_indicators:
                    print(f"         | ⚠️  Possible conflict detected: {', '.join(conflict_indicators)}")

                print()

                conflicts.append({
                    'id1': id1,
                    'id2': id2,
                    'similarity': sim,
                    'title1': title1,
                    'title2': title2,
                    'category1': cat1,
                    'category2': cat2,
                    'conflict_indicators': conflict_indicators
                })

            return conflicts

        return []

    def _detect_conflict_indicators(self, content1: str, content2: str) -> List[str]:
        """
        Detect potential conflicting statements using simple heuristics

        Returns list of conflict indicators found
        """
        indicators = []

        # Convert to lowercase for comparison
        c1 = content1.lower()
        c2 = content2.lower()

        # Look for contradictory patterns
        contradictions = [
            ('always', 'never'),
            ('always', 'avoid'),
            ('never', 'always'),
            ('avoid', 'use'),
            ('don\'t use', 'use'),
            ('recommended', 'not recommended'),
            ('best practice', 'antipattern'),
            ('fast', 'slow'),
            ('efficient', 'inefficient')
        ]

        for phrase1, phrase2 in contradictions:
            if phrase1 in c1 and phrase2 in c2:
                indicators.append(f"'{phrase1}' vs '{phrase2}'")
            elif phrase2 in c1 and phrase1 in c2:
                indicators.append(f"'{phrase2}' vs '{phrase1}'")

        # Look for different numeric values for same concept
        # (simplified - could be enhanced)
        if 'cost' in c1 and 'cost' in c2:
            if '$' in c1 and '$' in c2:
                indicators.append('different cost values')

        return indicators

    def find_fragmentation(self, min_count: int = FRAGMENTATION_COUNT) -> Dict[str, List]:
        """
        Find topics with multiple separate entries that should be consolidated

        Returns dict of {topic_keyword: [entry_ids]}
        """
        print(f"\n🔍 Finding fragmented topics ({min_count}+ entries on same topic)...")

        # Strategy: Group by common keywords in titles/tags
        fragmented = {}

        # Get all entries
        entries = self.con.execute("""
            SELECT id, title, category, tags
            FROM knowledge
            ORDER BY category, title
        """).fetchall()

        # Extract keywords from titles
        from collections import defaultdict
        keyword_entries = defaultdict(list)

        for entry_id, title, category, tags in entries:
            # Extract meaningful words from title (skip common words)
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            words = [w.lower() for w in title.split() if w.lower() not in stop_words and len(w) > 3]

            for word in words:
                keyword_entries[word].append({
                    'id': entry_id,
                    'title': title,
                    'category': category,
                    'tags': tags
                })

            # Also check tags
            if tags:
                for tag in tags:
                    if tag.startswith('layer:'):
                        continue  # Skip layer tags
                    keyword_entries[tag].append({
                        'id': entry_id,
                        'title': title,
                        'category': category,
                        'tags': tags
                    })

        # Find keywords with multiple entries
        for keyword, entries_list in keyword_entries.items():
            if len(entries_list) >= min_count:
                fragmented[keyword] = entries_list

        if fragmented:
            print(f"Found {len(fragmented)} fragmented topics:\n")

            for keyword, entries_list in sorted(fragmented.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"  '{keyword}' ({len(entries_list)} entries):")
                for entry in entries_list:
                    print(f"    - {entry['id']} | [{entry['category']}] {entry['title']}")
                print()

        return fragmented

    def find_orphans(self) -> List[Dict]:
        """Find entries with no tags, no links, or very little content"""
        print(f"\n🔍 Finding orphaned entries...")

        orphans = self.con.execute("""
            SELECT
                id,
                title,
                category,
                tags,
                LENGTH(content) as content_length,
                created,
                updated
            FROM knowledge
            WHERE (array_length(tags) = 0 OR tags IS NULL)
               OR LENGTH(content) < 100
            ORDER BY updated DESC
        """).fetchall()

        if orphans:
            print(f"Found {len(orphans)} orphaned entries:\n")

            orphan_list = []
            for row in orphans:
                entry_id, title, category, tags, content_len, created, updated = row

                issues = []
                if not tags or len(tags) == 0:
                    issues.append("no tags")
                if content_len < 100:
                    issues.append(f"short content ({content_len} chars)")

                print(f"  {entry_id}")
                print(f"    Title: {title}")
                print(f"    Issues: {', '.join(issues)}")
                print(f"    Updated: {updated}")
                print()

                orphan_list.append({
                    'id': entry_id,
                    'title': title,
                    'category': category,
                    'issues': issues,
                    'updated': str(updated)
                })

            return orphan_list

        return []

    def find_obsolete(self, days: int = OBSOLETE_DAYS) -> List[Dict]:
        """Find entries not updated in X days"""
        print(f"\n🔍 Finding obsolete entries (not updated in {days} days)...")

        cutoff_date = datetime.now() - timedelta(days=days)

        obsolete = self.con.execute(f"""
            SELECT
                id,
                title,
                category,
                updated,
                DATEDIFF('day', updated, CURRENT_TIMESTAMP) as days_old
            FROM knowledge
            WHERE updated < ?
            ORDER BY updated ASC
        """, [cutoff_date]).fetchall()

        if obsolete:
            print(f"Found {len(obsolete)} potentially obsolete entries:\n")

            obsolete_list = []
            for entry_id, title, category, updated, days_old in obsolete:
                print(f"  {entry_id} | {days_old} days old")
                print(f"    Title: {title}")
                print(f"    Last updated: {updated}")
                print()

                obsolete_list.append({
                    'id': entry_id,
                    'title': title,
                    'category': category,
                    'updated': str(updated),
                    'days_old': days_old
                })

            return obsolete_list

        return []

    def run_all_checks(self) -> Dict:
        """Run all defragmentation checks and return results"""
        print("=" * 60)
        print("Knowledge Base Defragmentation Analysis")
        print("=" * 60)

        results = {
            'duplicates': self.find_duplicates(),
            'conflicts': self.find_conflicts(),
            'fragmentation': self.find_fragmentation(),
            'orphans': self.find_orphans(),
            'obsolete': self.find_obsolete()
        }

        # Summary
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Duplicates: {len(results['duplicates'])}")
        print(f"Potential conflicts: {len(results['conflicts'])}")
        print(f"Fragmented topics: {len(results['fragmentation'])}")
        print(f"Orphaned entries: {len(results['orphans'])}")
        print(f"Obsolete entries: {len(results['obsolete'])}")

        total_issues = (
            len(results['duplicates']) +
            len(results['conflicts']) +
            len(results['fragmentation']) +
            len(results['orphans']) +
            len(results['obsolete'])
        )

        if total_issues == 0:
            print("\n✅ Knowledge base is well-organized!")
        else:
            print(f"\n⚠️  Found {total_issues} potential issues")
            print("\nRecommendations:")
            if results['duplicates']:
                print("  - Review duplicates and consolidate")
            if results['conflicts']:
                print("  - Check conflicts and resolve contradictions")
            if results['fragmentation']:
                print("  - Consider consolidating fragmented topics")
            if results['orphans']:
                print("  - Add tags or delete orphaned entries")
            if results['obsolete']:
                print("  - Review obsolete entries for relevance")

        return results

    def export_results(self, results: Dict, output_file: str):
        """Export results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results exported to: {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Defragment and analyze knowledge base',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--db-path',
        default='knowledge.duckdb',
        help='Path to DuckDB database'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Run all checks (default)'
    )

    parser.add_argument(
        '--duplicates',
        action='store_true',
        help='Find duplicate entries only'
    )

    parser.add_argument(
        '--conflicts',
        action='store_true',
        help='Find potential conflicts only'
    )

    parser.add_argument(
        '--fragmentation',
        action='store_true',
        help='Find fragmented topics only'
    )

    parser.add_argument(
        '--orphans',
        action='store_true',
        help='Find orphaned entries only'
    )

    parser.add_argument(
        '--obsolete',
        action='store_true',
        help='Find obsolete entries only'
    )

    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export results to JSON file'
    )

    args = parser.parse_args()

    # Default to --check if no specific check specified
    if not any([args.check, args.duplicates, args.conflicts, args.fragmentation, args.orphans, args.obsolete]):
        args.check = True

    # Check database exists
    if not Path(args.db_path).exists():
        print(f"ERROR: Database not found: {args.db_path}")
        return 1

    # Run analysis
    analyzer = DefragAnalyzer(args.db_path)

    if args.check:
        results = analyzer.run_all_checks()
    else:
        results = {}
        if args.duplicates:
            results['duplicates'] = analyzer.find_duplicates()
        if args.conflicts:
            results['conflicts'] = analyzer.find_conflicts()
        if args.fragmentation:
            results['fragmentation'] = analyzer.find_fragmentation()
        if args.orphans:
            results['orphans'] = analyzer.find_orphans()
        if args.obsolete:
            results['obsolete'] = analyzer.find_obsolete()

    # Export if requested
    if args.export:
        analyzer.export_results(results, args.export)

    return 0


if __name__ == '__main__':
    sys.exit(main())
