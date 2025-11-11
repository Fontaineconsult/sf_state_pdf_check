#!/usr/bin/env python3

import sqlite3


def is_archived(pdf_uri, parent_uri):
    """
    Check if a PDF should be marked as archived based on URL patterns.

    Args:
        pdf_uri: The URL to the PDF file
        parent_uri: The URL of the page hosting the PDF

    Returns:
        True if the PDF should be marked as archived, False otherwise
    """

    # Archive-related keywords to search for (case-insensitive)
    ARCHIVE_KEYWORDS = [
        'archive',
        'archived',
        'archives',
        'old-site',
        'old_site',
        'legacy',
        'deprecated',
        'obsolete',
        'superseded',
        'historical',
        'past-events',
        'past_events',
        'outdated'
    ]

    # Path segments that indicate archives
    ARCHIVE_PATHS = [
        '/old/',
        '/backup/',
        '/previous/',
        '/outdated/',
        '/archive/',
        '/archived/',
        '/legacy/',
        '/obsolete/',
        '/deprecated/'
    ]

    # Filename prefixes that indicate archives
    ARCHIVE_PREFIXES = [
        'archived_',
        'old_',
        'legacy_',
        'deprecated_',
        'obsolete_',
        'outdated_',
        'superseded_'
    ]

    # Filename suffixes that indicate archives
    ARCHIVE_SUFFIXES = [
        '_archived',
        '_old',
        '_legacy',
        '_deprecated',
        '_obsolete',
        '_outdated'
    ]

    # Check both URLs - if either is None/empty, treat as non-archived
    if not pdf_uri and not parent_uri:
        return False

    # Convert to lowercase for case-insensitive matching
    pdf_lower = pdf_uri.lower() if pdf_uri else ""
    parent_lower = parent_uri.lower() if parent_uri else ""

    # Extract filename from PDF URI
    filename = ""
    if pdf_uri:
        filename = pdf_uri.split('/')[-1].lower()
        # Remove file extension for suffix checking
        filename_no_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename

    # 1. Check for archive keywords in either URL
    for keyword in ARCHIVE_KEYWORDS:
        if keyword in pdf_lower or keyword in parent_lower:
            return True

    # 2. Check for archive path segments
    for path in ARCHIVE_PATHS:
        if path in pdf_lower or path in parent_lower:
            return True

    # 3. Check filename prefixes
    for prefix in ARCHIVE_PREFIXES:
        if filename.startswith(prefix):
            return True

    # 4. Check filename suffixes (without extension)
    if filename:
        filename_no_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        for suffix in ARCHIVE_SUFFIXES:
            if filename_no_ext.endswith(suffix):
                return True

    # If no archive patterns found, return False
    return False


def update_database():
    """
    Query all records from drupal_pdf_files and update pdf_is_archived field.
    """
    # Connect to database
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    # First, reset all pdf_is_archived flags to 0
    print("Resetting all pdf_is_archived flags to 0...")
    cursor.execute("UPDATE drupal_pdf_files SET pdf_is_archived = 0")
    conn.commit()
    print("Reset complete. Starting fresh scan...")

    # Get all records
    cursor.execute("SELECT id, pdf_uri, parent_uri FROM drupal_pdf_files")
    records = cursor.fetchall()

    print(f"Processing {len(records)} records...")

    # Counter for updated records
    updated_count = 0

    # Process each record
    for pdf_id, pdf_uri, parent_uri in records:
        # Check if archived
        if is_archived(pdf_uri, parent_uri):
            # Only update if it should be archived (already set all to 0)
            cursor.execute("UPDATE drupal_pdf_files SET pdf_is_archived = 1 WHERE id = ?",
                          (pdf_id,))
            updated_count += 1

    # Commit changes
    conn.commit()
    conn.close()

    print(f"Completed: {updated_count} records marked as archived out of {len(records)} total")


if __name__ == "__main__":
    update_database()