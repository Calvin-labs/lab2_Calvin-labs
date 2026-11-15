#!/bin/bash
# organizer.sh - archives grades.csv with a timestamp, creates a new empty
# grades.csv, and appends the details to organizer.log (accumulates every run).

CSV_FILE="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

if [ ! -f "$CSV_FILE" ]; then
    echo "Error: $CSV_FILE not found in $(pwd). Nothing to archive."
    exit 1
fi

# Create the archive directory if it does not exist
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir "$ARCHIVE_DIR" || { echo "Error: could not create $ARCHIVE_DIR directory."; exit 1; }
fi

TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
NEW_NAME="grades_${TIMESTAMP}.csv"

# Rename (move) grades.csv into the archive with the timestamp appended
if ! mv "$CSV_FILE" "$ARCHIVE_DIR/$NEW_NAME"; then
    echo "Error: could not archive $CSV_FILE."
    exit 1
fi

# Workspace reset: new, empty grades.csv
: > "$CSV_FILE"

# Log: timestamp, original filename, new archived filename
echo "$(date '+%Y-%m-%d %H:%M:%S') | original: $CSV_FILE | archived as: $ARCHIVE_DIR/$NEW_NAME" >> "$LOG_FILE"

echo "Archived $CSV_FILE -> $ARCHIVE_DIR/$NEW_NAME"
echo "Created new empty $CSV_FILE"
echo "Logged to $LOG_FILE"
