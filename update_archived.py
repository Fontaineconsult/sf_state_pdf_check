#!/usr/bin/env python3

import sqlite3
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sf_state_pdf_scan.sf_state_pdf_scan.box_handler import get_box_contents


def is_archived(pdf_uri, parent_uri, box_filename=None):
    """
    Check if a PDF should be marked as archived based on URL patterns and filename.

    Args:
        pdf_uri: The URL to the PDF file
        parent_uri: The URL of the page hosting the PDF
        box_filename: Optional filename from Box (e.g., "Fall-2020-Archive.pdf")

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

    # 5. Check Box filename if provided (for Box share links where URL doesn't contain filename)
    if box_filename:
        box_filename_lower = box_filename.lower()
        box_filename_no_ext = box_filename_lower.rsplit('.', 1)[0] if '.' in box_filename_lower else box_filename_lower

        # Check keywords in Box filename
        for keyword in ARCHIVE_KEYWORDS:
            if keyword in box_filename_lower:
                return True

        # Check prefixes in Box filename
        for prefix in ARCHIVE_PREFIXES:
            if box_filename_lower.startswith(prefix):
                return True

        # Check suffixes in Box filename (without extension)
        for suffix in ARCHIVE_SUFFIXES:
            if box_filename_no_ext.endswith(suffix):
                return True

    # If no archive patterns found, return False
    return False


def get_pdfs_after_archive_sections(page_url):
    """
    Fetch a page and return all PDF URLs that appear after archive sections.

    Args:
        page_url: URL of the page to check

    Returns:
        List of PDF URLs found after archive sections
    """
    try:
        # Fetch the page
        response = requests.get(page_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        pdf_urls = []
        archive_keywords = ['archive', 'archived', 'archives', 'archival', 'archiving']
        # Updated Box URL pattern to be more flexible
        box_url_pattern = re.compile(r'https?://[a-zA-Z0-9.-]*\.box\.com/s/[a-zA-Z0-9]+', re.IGNORECASE)

        # Find all archive markers (headings and paragraphs)
        archive_markers = []

        # Check headings (h1, h2, h3, h4, h5, h6)
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(tag):
                if heading.text:
                    text_lower = heading.text.lower()
                    if any(keyword in text_lower for keyword in archive_keywords):
                        archive_markers.append(heading)
                        print(f"  Found archive marker: {tag} - {heading.text.strip()[:50]}")

        # Check paragraphs for "Archived Content:"
        for p in soup.find_all('p'):
            if p.text and 'archived content:' in p.text.lower():
                archive_markers.append(p)
                print(f"  Found archive marker: p - {p.text.strip()[:50]}")

        print(f"  Total archive markers found: {len(archive_markers)}")

        # For each archive marker, collect PDFs until next section
        for marker in archive_markers:
            # Get heading level if it's a heading
            if marker.name.startswith('h'):
                level = int(marker.name[1])
            else:
                level = 6  # Treat paragraphs as lowest level

            # Find all elements after this marker
            for element in marker.find_all_next():
                # Stop at next heading of same or higher level
                if element.name and element.name.startswith('h'):
                    element_level = int(element.name[1])
                    if element_level <= level:
                        break

                # Check for links
                if element.name == 'a':
                    href = element.get('href')
                    if href:
                        absolute_url = urljoin(page_url, href)

                        # Check if it's a PDF link
                        if '.pdf' in href.lower():
                            if absolute_url not in pdf_urls:
                                pdf_urls.append(absolute_url)
                                print(f"    Added PDF: {absolute_url}")

                        # Check if it's a Box link
                        elif box_url_pattern.match(absolute_url):
                            if absolute_url not in pdf_urls:  # Check before calling get_box_contents
                                try:
                                    print(f"    Checking Box link: {absolute_url}")
                                    box_result = get_box_contents(absolute_url)
                                    if box_result and len(box_result) > 0 and box_result[0]:  # It's a PDF in Box
                                        pdf_urls.append(absolute_url)
                                        print(f"    Added Box PDF: {absolute_url} - {box_result[2] if len(box_result) > 2 else 'Unknown name'}")
                                    else:
                                        print(f"    Box link not a PDF or error: {box_result[1] if box_result and len(box_result) > 1 else 'Unknown error'}")
                                except Exception as e:
                                    print(f"    Error checking Box link {absolute_url}: {str(e)}")

                # Check nested links
                elif hasattr(element, 'find_all'):
                    for link in element.find_all('a', href=True):
                        href = link.get('href')
                        if href:
                            absolute_url = urljoin(page_url, href)

                            # Check if it's a PDF link
                            if '.pdf' in href.lower():
                                if absolute_url not in pdf_urls:
                                    pdf_urls.append(absolute_url)
                                    print(f"    Added nested PDF: {absolute_url}")

                            # Check if it's a Box link
                            elif box_url_pattern.match(absolute_url):
                                if absolute_url not in pdf_urls:  # Check before calling get_box_contents
                                    try:
                                        print(f"    Checking nested Box link: {absolute_url}")
                                        box_result = get_box_contents(absolute_url)
                                        if box_result and len(box_result) > 0 and box_result[0]:  # It's a PDF in Box
                                            pdf_urls.append(absolute_url)
                                            print(f"    Added nested Box PDF: {absolute_url} - {box_result[2] if len(box_result) > 2 else 'Unknown name'}")
                                        else:
                                            print(f"    Nested Box link not a PDF or error: {box_result[1] if box_result and len(box_result) > 1 else 'Unknown error'}")
                                    except Exception as e:
                                        print(f"    Error checking nested Box link {absolute_url}: {str(e)}")

        return pdf_urls

    except Exception as e:
        print(f"Error processing page {page_url}: {str(e)}")
        return []



def refresh_parent_urls_archived_status(parent_url=None):
    """
    Execute the get_all_parent_sites.sql query and run get_pdfs_after_archive_sections
    for each parent domain, or process a single parent URL if provided.
    Updates the database to mark found PDFs as archived.

    Args:
        parent_url (str, optional): Single parent URL to process. If not provided,
                                    queries database for all parent URLs.
    """
    # Connect to database (needed for both single URL and multiple URLs)
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    total_pdfs_marked = 0

    # Helper function to update PDFs as archived
    def mark_pdfs_as_archived(pdf_urls, parent_uri):
        """Update database to mark PDFs as archived."""
        updated_count = 0
        box_url_pattern = re.compile(r'https?://(?:sfsu\.app\.box\.com|sfsu\.box\.com)/s/([a-zA-Z0-9]+)', re.IGNORECASE)

        for pdf_url in pdf_urls:
            # Check if it's a Box URL
            box_match = box_url_pattern.match(pdf_url)

            if box_match:
                # For Box URLs, check both variations
                box_id = box_match.group(1)
                cursor.execute("""
                    UPDATE drupal_pdf_files
                    SET pdf_is_archived = 1
                    WHERE (pdf_uri = ? OR pdf_uri = ? OR pdf_uri = ?) AND parent_uri = ?
                """, (
                    pdf_url,  # Original URL
                    f"https://sfsu.app.box.com/s/{box_id}",  # app.box.com variant
                    f"https://sfsu.box.com/s/{box_id}",  # box.com variant
                    parent_uri
                ))

                rows_affected = cursor.rowcount
                if rows_affected > 0:
                    updated_count += rows_affected
                    print(f"    - Marked as archived (Box URL with {rows_affected} matches): {pdf_url}")
                else:
                    print(f"    - Not found in DB or already archived (Box URL): {pdf_url}")
            else:
                # For regular PDFs, use exact match
                cursor.execute("""
                    UPDATE drupal_pdf_files
                    SET pdf_is_archived = 1
                    WHERE pdf_uri = ? AND parent_uri = ?
                """, (pdf_url, parent_uri))

                rows_affected = cursor.rowcount
                if rows_affected > 0:
                    updated_count += rows_affected
                    print(f"    - Marked as archived: {pdf_url}")
                else:
                    print(f"    - Not found in DB or already archived: {pdf_url}")

        conn.commit()
        return updated_count

    # If a single parent URL is provided, process only that
    if parent_url:
        print(f"Processing single URL: {parent_url}")
        pdf_urls = get_pdfs_after_archive_sections(parent_url)

        if pdf_urls:
            print(f"  Found {len(pdf_urls)} PDFs in archive sections")
            updated = mark_pdfs_as_archived(pdf_urls, parent_url)
            total_pdfs_marked += updated
            print(f"  Updated {updated} PDFs in database")
        else:
            print(f"  No PDFs found in archive sections")

        conn.close()
        print(f"Completed processing single URL. Total PDFs marked as archived: {total_pdfs_marked}")
        return

    # Otherwise, query the database for all parent sites
    # Execute the SQL query from get_all_parent_sites.sql
    cursor.execute("""
        SELECT parent_uri FROM drupal_pdf_files
        WHERE parent_returns_404 = false
        GROUP BY parent_uri
    """)

    parent_sites = cursor.fetchall()
    print(f"Found {len(parent_sites)} unique parent sites to process")

    # Process each parent domain
    processed_sites = 0
    for (parent_uri,) in parent_sites:
        if parent_uri:  # Make sure the URL is not None or empty
            processed_sites += 1
            print(f"[{processed_sites}/{len(parent_sites)}] Processing: {parent_uri}")
            pdf_urls = get_pdfs_after_archive_sections(parent_uri)

            if pdf_urls:
                print(f"  Found {len(pdf_urls)} PDFs in archive sections")
                updated = mark_pdfs_as_archived(pdf_urls, parent_uri)
                total_pdfs_marked += updated
                print(f"  Updated {updated} PDFs in database")
            else:
                print(f"  No PDFs found in archive sections")

    conn.close()
    print(f"\nCompleted processing all parent sites.")
    print(f"Total PDFs marked as archived: {total_pdfs_marked}")




def update_archives():
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

    refresh_parent_urls_archived_status()

    print(f"Completed: {updated_count} records marked as archived out of {len(records)} total")


if __name__ == "__main__":
    update_archives()
