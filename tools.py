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

def strip_trailing_items_from_pdf_urls():
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    pdfs = cursor.execute("SELECT * FROM drupal_pdf_files").fetchall()

    for each in pdfs:
        original_url = each[1]
        # print(each[1])
        # Remove everything after the first space (if any)
        cleaned_url = original_url.split(" ")[0]

        # If the URL has been changed, update the record
        if cleaned_url != original_url:
            print(f"Updating: {original_url} -> {cleaned_url}")
            # Assuming 'id' is the primary key and is stored in the first column.
            cursor.execute("UPDATE drupal_pdf_files SET pdf_uri = ? WHERE id = ?", (cleaned_url, each[0]))

    conn.commit()
    conn.close()

import sqlite3

def delete_duplicate_entries():
    """
    For each site in the drupal_site table, this function reads the SQL query from
    delete_duplicates.sql (which deletes duplicate PDF entries for a given site by keeping only the oldest scan),
    substitutes the {site_name} placeholder with the actual domain name, and executes the query.

    The site names are retrieved by executing the SQL query stored in get_all_sites.sql.
    """
    # Connect to the SQLite database.
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    # Read the get_all_sites.sql file, which contains:
    # select domain_name from drupal_site;
    with open("sql/get_all_sites.sql", "r") as f:
        get_sites_query = f.read().strip()

    # Execute the query to fetch all site domain names.
    cursor.execute(get_sites_query)
    sites = cursor.fetchall()  # Each row is a tuple (domain_name,)

    # Read the delete_duplicates.sql file which contains our delete query template.
    with open("sql/delete_duplicates.sql", "r") as f:
        delete_query_template = f.read()

    # Loop through each site and execute the delete query with the proper substitution.
    for site in sites:
        domain_name = site[0]
        formatted_query = delete_query_template.replace("{site_name}", domain_name)
        print(f"Deleting duplicate entries for site: {domain_name}")
        cursor.executescript(formatted_query)
        conn.commit()
        print(f"Finished processing site: {domain_name}")

    # Close the database connection.
    conn.close()

# Example usage:
delete_duplicate_entries()
