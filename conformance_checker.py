import os
import sqlite3

import time
from urllib.parse import urlparse, urlunparse, quote

import requests
import subprocess

from data_export import get_all_sites, get_pdf_reports_by_site_name
from data_import import add_pdf_file_to_database, get_site_id_by_domain_name, check_if_pdf_report_exists, \
    add_pdf_report_failure
from pdf_priority import violation_counter, pdf_check, pdf_status
from sf_state_pdf_scan.sf_state_pdf_scan.box_handler import box_share_pattern_match, download_from_box
from set_env import get_project_path, get_database_path
from update_archived import is_archived


temp_pdf_path = get_project_path('temp_pdf')
COMPLETED_CONFORMANCE_FILE = get_project_path('completed_conformance')


def load_completed_conformance():
    """Load the set of completed PDF scans from tracking file."""
    if not os.path.exists(COMPLETED_CONFORMANCE_FILE):
        return set()
    with open(COMPLETED_CONFORMANCE_FILE, encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}


def mark_conformance_completed(pdf_uri, parent_uri):
    """Mark a PDF as scanned by appending to tracking file."""
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(COMPLETED_CONFORMANCE_FILE), exist_ok=True)
    key = f"{pdf_uri} {parent_uri}"
    with open(COMPLETED_CONFORMANCE_FILE, 'a', encoding='utf-8') as f:
        f.write(key + '\n')


def is_conformance_completed(pdf_uri, parent_uri, completed_set):
    """Check if a PDF has already been scanned in this session."""
    key = f"{pdf_uri} {parent_uri}"
    return key in completed_set


def get_conformance_progress():
    """Get the count of completed conformance scans."""
    completed = load_completed_conformance()
    return len(completed)


temp_profile_path = get_project_path('temp_profile')

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_pdf_into_memory(url, loc, domain_id, timeout=30, allow_insecure_retry=True):
    import urllib3
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.SSLError as e:
        if not allow_insecure_retry:
            add_pdf_report_failure(url, loc, domain_id, f"SSL error: {e}")
            return False
        # Retry without certificate verification
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, verify=False)
            resp.raise_for_status()
            return resp.content
        except requests.exceptions.RequestException as e2:
            status = f"{getattr(e2, 'response', None).status_code} " if getattr(e2, 'response', None) is not None else ""
            add_pdf_report_failure(url, loc, domain_id, f"Couldn't download (insecure retry) {status}{e2}")
            return False
    except requests.exceptions.RequestException as e:
        status = f"{getattr(e, 'response', None).status_code} " if getattr(e, 'response', None) is not None else ""
        add_pdf_report_failure(url, loc, domain_id, f"Couldn't download {status}{e}")
        return False


def create_verapdf_report(url):

    try:
        verapdf_command = f'verapdf -f ua1 --format json "{temp_pdf_path}" > "{temp_profile_path}"'

        # Execute the command and capture the output
        try:
            subprocess.run(verapdf_command, shell=True, text=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("Failed to create report", url, e)
            print(e.output)

        violations = violation_counter(temp_profile_path)
        violations.update(pdf_check(temp_pdf_path))
        return {"report": {"report": violations, "status": "Succeeded"}}
    except KeyError as e:
        print("Failed to create report", url, e)
        return {"report": {"report": "", "status": "Failed"}}



def load_text_file_lines(file_path):
    with open(file_path) as f:
        return f.read().splitlines()


def loop_through_files_in_folder(folder_path):
    file_path = os.path.join(folder_path, "scanned_pdfs.txt")
    if os.path.exists(file_path):
        return load_text_file_lines(file_path)
    return None  # Return None if the file does not exist


def scan_pdfs(directory, domain_id, completed_set=None):

    """
    Scans PDF files listed in text files within a specified directory and generates accessibility reports.

    Parameters:
    directory (str): The path to the directory containing text files with PDF URLs and their locations.
    domain_id (int): The ID of the domain associated with the PDFs.
    completed_set (set): Optional set of already completed scans for resume capability.

    Process:
    1. Loads the list of PDF URLs and their locations from text files in the specified directory.
    2. For each PDF URL and location:
        a. Checks if scan was already completed in this session (resume support).
        b. Checks if an accessibility report already exists for the PDF.
        c. If no report exists, downloads the PDF.
        d. Generates an accessibility report using VeraPDF.
        e. Adds the report to the database if successful, or logs a failure if not.
        f. Marks the PDF as completed in the tracking file.
    """

    pdf_locations = loop_through_files_in_folder(directory)

    if pdf_locations:
        total_pdfs = len(pdf_locations)

        for idx, file in enumerate(pdf_locations, 1):
            print(f"[{idx}/{total_pdfs}]", file)

            try:
                file_split = file.split(' ', 1)  # Splits at the last space

                file_url = file_split[0]
                loc = file_split[1].split(" ")[0]
                print("checking", file_url, loc)

                # Skip if already completed in this session
                if completed_set and is_conformance_completed(file_url, loc, completed_set):
                    print("Already scanned in this session, skipping", file_url)
                    continue

                # parsed_url = urlparse(file_url)
                # encoded_path = quote(parsed_url.path)
                # file_url = urlunparse(parsed_url._replace(path=encoded_path))
                report_exsits = check_if_pdf_report_exists(file_url, loc) # report will exist if there is a hash match
            except ValueError as e:
                add_pdf_report_failure("file_url", "loc", domain_id, "Couldn't unpack file url and location")
                continue

            if not report_exsits:
                print("Report does not exist", file_url, loc)
                box_filename = None  # Track Box filename for archive checking

                if box_share_pattern_match(file_url):
                    print("Downloading File From Box")
                    box_download = download_from_box(file_url, loc, domain_id) # saved to temp_pdf_path

                    if not box_download[0]:
                        print("Box Download failed", file_url)
                        add_pdf_report_failure(file_url, loc, domain_id, box_download[1])
                        mark_conformance_completed(file_url, loc)  # Mark as completed even on failure
                        continue

                    # Capture Box filename for archive checking
                    box_filename = box_download[2] if len(box_download) > 2 else None
                else:
                    pdf_download = download_pdf_into_memory(file_url,loc, domain_id) # saved to temp_pdf_path
                    if pdf_download:

                        with open(temp_pdf_path, "wb") as f:
                            f.write(pdf_download)
                    else:
                        mark_conformance_completed(file_url, loc)  # Mark as completed even on failure
                        continue

                report = create_verapdf_report(file_url) # default looks to temp_pdf_path

                if report["report"]["status"] == "Succeeded":
                    # Check if PDF should be marked as archived (using Box filename if available)
                    pdf_is_archived = is_archived(file_url, loc, box_filename)
                    add_pdf_file_to_database(file_url, loc, domain_id, report["report"]["report"], pdf_is_archived=pdf_is_archived)
                else:
                    add_pdf_report_failure(file_url, loc, domain_id, report["report"]["report"])

                # Mark as completed after processing
                mark_conformance_completed(file_url, loc)

            else:
                print("Report already exists", file_url)
                mark_conformance_completed(file_url, loc)  # Mark as completed
                continue


def mark_replaced_pdfs_as_removed(domain_id):

    with open("sql/update_scan_by_removing_old_duplicates.sql", "r") as file:
        query = file.read()

    formatted_query = query.format(site_name=domain_id)
    print(formatted_query)
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    cursor.execute(formatted_query)


def refresh_existing_pdf_reports(single_domain=None):

    # this will redownload all PDFs and regenerate reports

    def scan_pdfs_by_domain(domain):

        site_data = get_pdf_reports_by_site_name(domain)
        if site_data:
            for row in site_data:
                print(row.pdf_uri)
                box_filename = None  # Track Box filename for archive checking

                if box_share_pattern_match(row.pdf_uri):
                    print("Downloading File From Box")
                    box_download = download_from_box(row.pdf_uri, 'None', "None")

                    if not box_download[0]:
                        print("Box Download failed", row.pdf_uri)
                        add_pdf_report_failure(row.pdf_uri, row.parent_uri, row.drupal_site_id, box_download[1])
                        continue

                    # Capture Box filename for archive checking
                    box_filename = box_download[2] if len(box_download) > 2 else None
                else:
                    pdf_download = download_pdf_into_memory(row.pdf_uri, row.parent_uri, row.drupal_site_id)
                    if pdf_download:
                        with open(temp_pdf_path, "wb") as f:
                            f.write(pdf_download)
                    else:
                        continue

                report = create_verapdf_report(row.pdf_uri) # default looks to temp_pdf_path

                if report["report"]["status"] == "Succeeded":
                    print("Add report to DB")
                    # Check if PDF should be marked as archived (using Box filename if available)
                    pdf_is_archived = is_archived(row.pdf_uri, row.parent_uri, box_filename)
                    add_pdf_file_to_database(row.pdf_uri, row.parent_uri, row.drupal_site_id, report["report"]["report"], overwrite=True, pdf_is_archived=pdf_is_archived)
                else:
                    add_pdf_report_failure(row.pdf_uri, row.parent_uri, row.drupal_site_id, report["report"]["report"])




    if not single_domain:
        # refresh all sites
        all_sites_list = get_all_sites()
        print(all_sites_list)
        for domain in all_sites_list:
            scan_pdfs_by_domain(domain)
            mark_replaced_pdfs_as_removed(domain)

    if single_domain:
        #refresh single domain
        scan_pdfs_by_domain(single_domain)
        mark_replaced_pdfs_as_removed(single_domain)





def enable_wal_mode():
    """Enable SQLite WAL mode for better concurrency."""
    conn = sqlite3.connect(get_database_path())
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.commit()
    conn.close()
    print("SQLite WAL mode enabled")


def full_pdf_scan(site_folders):
    """
    Scans all subdirectories within the given directory for PDF files and generates accessibility reports.

    Parameters:
    site_folders (str): The path to the directory containing subdirectories to be scanned.

    Process:
    1. Enables WAL mode for better database concurrency.
    2. Loads completed scans from tracking file for resume capability.
    3. Iterates over each folder (subdirectory) within the `site_folders` directory.
    4. Retrieves the domain ID for each folder by calling `get_site_id_by_domain_name`.
    5. If a valid domain ID is found, calls the `scan_pdfs` function, passing the path to the current folder and the domain ID as arguments.
    """
    # Enable WAL mode for better concurrency
    enable_wal_mode()

    # Load completed scans for resume capability
    completed_set = load_completed_conformance()
    print(f"Loaded {len(completed_set)} previously completed scans")

    for folder in os.listdir(site_folders):

        domain_id = get_site_id_by_domain_name(folder)
        print(folder, domain_id, os.path.join(site_folders, folder))
        if domain_id is not None:
            scan_pdfs(os.path.join(site_folders, folder), domain_id, completed_set)



def single_site_pdf_scan(site_folder):
    """
    Scans a single subdirectory for PDF files and generates accessibility reports.

    Parameters:
    site_folder (str): The path to the subdirectory to be scanned.

    Process:
    1. Loads completed scans from tracking file for resume capability.
    2. Retrieves the domain ID for the folder by calling `get_site_id_by_domain_name`.
    3. If a valid domain ID is found, calls the `scan_pdfs` function, passing the path to the folder and the domain ID as arguments.
    """
    # Load completed scans for resume capability
    completed_set = load_completed_conformance()
    print(f"Loaded {len(completed_set)} previously completed scans")

    domain_id = get_site_id_by_domain_name(os.path.basename(site_folder))

    if domain_id is not None:
        scan_pdfs(site_folder, domain_id, completed_set)

#
if __name__=='__main__':

    mark_replaced_pdfs_as_removed("socwork.sfsu.edu")