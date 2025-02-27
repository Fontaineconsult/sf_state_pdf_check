#!/usr/bin/env python3
import os
import sqlite3


def delete_scans_files(root_folder):
    # Walk through the directory tree
    for current_path, dirs, files in os.walk(root_folder):
        for file in files:
            # Check if the file name contains the substring
            if "_scans.xlsx" in file:
                file_path = os.path.join(current_path, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


def remove_timestamps_from_parent_urls():
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    pdfs = cursor.execute("SELECT * FROM drupal_pdf_files").fetchall()

    for each in pdfs:
        original_url = each[2]
        print(each[0])
        # Remove everything after the first space (if any)
        cleaned_url = original_url.split(" ")[0]

        # If the URL has been changed, update the record
        if cleaned_url != original_url:
            print(f"Updating: {original_url} -> {cleaned_url}")
            # Assuming 'id' is the primary key and is stored in the first column.
            cursor.execute("UPDATE drupal_pdf_files SET parent_uri = ? WHERE id = ?", (cleaned_url, each[0]))

    conn.commit()
    conn.close()

