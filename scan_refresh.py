import sqlite3
import requests

from sf_state_pdf_scan.sf_state_pdf_scan.box_handler import box_share_pattern_match, download_from_box


def refresh_status():
    """
    Loop through all PDFs and their parent URIs, making HTTP HEAD requests to check their status.
    For PDF URIs that are Box share links, obtain the direct download URL using download_from_box (head=True)
    and perform the HEAD request on that URL.
    If a URL returns a 404 (or cannot be reached), set the corresponding flag in the database.
    """
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    pdfs = cursor.execute("SELECT * FROM drupal_pdf_files").fetchall()

    total_records = len(pdfs)
    print(f"Total records found: {total_records}")

    for i, each in enumerate(pdfs, start=1):
        pdf_id = each[0]
        pdf_uri = each[1]
        pdf_parent = each[2]

        print(f"\nProcessing record {i}/{total_records}: ID {pdf_id}")

        # Skip problematic URIs if they contain spaces (indicating possible formatting issues)
        if len(pdf_uri.split(" ")) > 1 or len(pdf_parent.split(" ")) > 1:
            print(f"Skipping problematic URIs for ID {pdf_id}: '{pdf_uri}', '{pdf_parent}'")
            continue

        # Check PDF URL status
        if box_share_pattern_match(pdf_uri):
            # PDF URI is a Box share link
            print(f"PDF URI is a Box share link: {pdf_uri}")
            download_url = download_from_box(pdf_uri, loc="", domain_id=None, head=True)
            if not isinstance(download_url, str) or not download_url:
                print(f"Failed to obtain download link for Box share: {pdf_uri}")
                cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (1, pdf_id))
            else:
                print(f"Checking Box PDF download URL: {download_url}")
                try:
                    box_response = requests.head(download_url, timeout=10)
                    print(f"Box PDF download URL status code: {box_response.status_code}")
                    if box_response.status_code == 404:
                        cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (1, pdf_id))
                    else:
                        cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (0, pdf_id))
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching Box PDF download URL ({download_url}): {e}")
                    cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (1, pdf_id))
        else:
            # Regular PDF URI (not a Box link)
            try:
                print(f"Checking PDF URL: {pdf_uri}")
                pdf_response = requests.head(pdf_uri, timeout=10)
                print(f"PDF URL status code: {pdf_response.status_code}")
                if pdf_response.status_code == 404:
                    cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (1, pdf_id))
                else:
                    cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (0, pdf_id))
            except requests.exceptions.RequestException as e:
                print(f"Error fetching PDF URL ({pdf_uri}): {e}")
                cursor.execute("UPDATE drupal_pdf_files SET pdf_returns_404 = ? WHERE id = ?", (1, pdf_id))

        # Check Parent URL status using HEAD request
        try:
            print(f"Checking Parent URL: {pdf_parent}")
            parent_response = requests.head(pdf_parent, timeout=10)
            print(f"Parent URL status code: {parent_response.status_code}")
            if parent_response.status_code == 404:
                cursor.execute("UPDATE drupal_pdf_files SET parent_returns_404 = ? WHERE id = ?", (1, pdf_id))
            else:
                cursor.execute("UPDATE drupal_pdf_files SET parent_returns_404 = ? WHERE id = ?", (0, pdf_id))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Parent URL ({pdf_parent}): {e}")
            cursor.execute("UPDATE drupal_pdf_files SET parent_returns_404 = ? WHERE id = ?", (1, pdf_id))

        print(f"Finished processing record ID {pdf_id}")

    conn.commit()
    print("\nAll records processed. Changes committed to the database.")
    conn.close()
    print("Database connection closed.")