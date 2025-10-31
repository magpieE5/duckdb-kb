#!/bin/bash
# DuckDB Knowledge Base Backup Script
#
# This script creates timestamped backups of the knowledge.duckdb file
# and maintains a rolling window of backups to prevent disk bloat.
#
# Usage: ./backup.sh [--keep-days N]
#   --keep-days N: Keep backups from the last N days (default: 30)

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_FILE="${SCRIPT_DIR}/knowledge.duckdb"
BACKUP_DIR="${SCRIPT_DIR}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
KEEP_DAYS=30

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-days)
            KEEP_DAYS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--keep-days N]"
            exit 1
            ;;
    esac
done

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if database exists
if [ ! -f "${DB_FILE}" ]; then
    echo "Error: Database file not found: ${DB_FILE}"
    exit 1
fi

# Get database size
DB_SIZE=$(du -h "${DB_FILE}" | cut -f1)

# Create backup with timestamp
BACKUP_FILE="${BACKUP_DIR}/knowledge_${TIMESTAMP}.duckdb"
echo "Creating backup..."
echo "  Source: ${DB_FILE} (${DB_SIZE})"
echo "  Destination: ${BACKUP_FILE}"

cp "${DB_FILE}" "${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup created successfully: ${BACKUP_SIZE}"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Get database stats using DuckDB
echo ""
echo "Database statistics:"
duckdb "${BACKUP_FILE}" <<SQL
SELECT
    COUNT(*) as total_entries,
    COUNT(embedding) as entries_with_embeddings,
    COUNT(DISTINCT category) as categories
FROM knowledge;
SQL

# Clean up old backups
echo ""
echo "Cleaning up backups older than ${KEEP_DAYS} days..."
find "${BACKUP_DIR}" -name "knowledge_*.duckdb" -type f -mtime +${KEEP_DAYS} -print -delete

# Show remaining backups
echo ""
echo "Current backups:"
ls -lh "${BACKUP_DIR}"/knowledge_*.duckdb | tail -10

# Calculate total backup size
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
echo ""
echo "Total backup directory size: ${TOTAL_SIZE}"
echo "✅ Backup complete!"
