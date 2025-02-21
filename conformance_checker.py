import os
import time
from urllib.parse import urlparse, urlunparse, quote

import requests
import subprocess

from data_import import add_pdf_file_to_database, get_site_id_by_domain_name, check_if_pdf_report_exists, \
    add_pdf_report_failure
from pdf_priority import violation_counter, pdf_check, pdf_status
from sf_state_pdf_scan.sf_state_pdf_scan.box_handler import box_share_pattern_match, download_from_box


temp_pdf_path = "C:\\Users\\913678186\\IdeaProjects\\sf_state_pdf_website_scan\\temp\\temp.pdf"
temp_profile_path = "C:\\Users\\913678186\\IdeaProjects\\sf_state_pdf_website_scan\\temp\\temp_profile.json"

def download_pdf_into_memory(url, loc, domain_id):

    request = requests.get(url)
    print("DFDSFDS", request, url)
    if request.ok:
        return request.content
    else:
        add_pdf_report_failure(url, loc, domain_id, f"Couldn't download {request.status_code}")
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


def scan_pdfs(directory, domain_id):

    """
    Scans PDF files listed in text files within a specified directory and generates accessibility reports.

    Parameters:
    directory (str): The path to the directory containing text files with PDF URLs and their locations.
    domain_id (int): The ID of the domain associated with the PDFs.

    Process:
    1. Loads the list of PDF URLs and their locations from text files in the specified directory.
    2. For each PDF URL and location:
        a. Checks if an accessibility report already exists for the PDF.
        b. If no report exists, downloads the PDF.
        c. Generates an accessibility report using VeraPDF.
        d. Adds the report to the database if successful, or logs a failure if not.
    """

    pdf_locations = loop_through_files_in_folder(directory)

    if pdf_locations:

        for file in pdf_locations:
            print("DFD", file)

            try:
                file_split = file.split(' ', 1)  # Splits at the last space
                print(file_split)
                file_url = file_split[0]
                loc = file_split[1]


                # parsed_url = urlparse(file_url)
                # encoded_path = quote(parsed_url.path)
                # file_url = urlunparse(parsed_url._replace(path=encoded_path))
                report_exsits = check_if_pdf_report_exists(file_url, loc)
                print("report exists", report_exsits)
            except ValueError as e:
                add_pdf_report_failure("file_url", "loc", domain_id, "Couldn't unpack file url and location")
                continue

            if not report_exsits:
                if box_share_pattern_match(file_url):
                    print("Downloading File From Box")
                    box_download = download_from_box(file_url, loc, domain_id)

                    if not box_download[0]:
                        print("Box Download failed", file_url)
                        add_pdf_report_failure(file_url, loc, domain_id, box_download[1])
                else:
                    pdf_download = download_pdf_into_memory(file_url,loc, domain_id)
                    if pdf_download:

                        with open(temp_pdf_path, "wb") as f:
                            f.write(pdf_download)
                    else:
                        continue

                report = create_verapdf_report(file_url)

                if report["report"]["status"] == "Succeeded":
                    print("Add report to DB")
                    add_pdf_file_to_database(file_url, loc, domain_id, report["report"]["report"])
                else:
                    add_pdf_report_failure(file_url, loc, domain_id, report["report"]["report"])

            else:
                print("Report already exists", file_url)
                continue


def full_pdf_scan(site_folders):
    """
    Scans all subdirectories within the given directory for PDF files and generates accessibility reports.

    Parameters:
    site_folders (str): The path to the directory containing subdirectories to be scanned.

    Process:
    1. Iterates over each folder (subdirectory) within the `site_folders` directory.
    2. Retrieves the domain ID for each folder by calling `get_site_id_by_domain_name`.
    3. If a valid domain ID is found, calls the `scan_pdfs` function, passing the path to the current folder and the domain ID as arguments.
    """
    for folder in os.listdir(site_folders):

        domain_id = get_site_id_by_domain_name(folder)
        print(folder, domain_id, os.path.join(site_folders, folder))
        if domain_id is not None:
            scan_pdfs(os.path.join(site_folders, folder), domain_id)



def single_site_pdf_scan(site_folder):
    """
    Scans a single subdirectory for PDF files and generates accessibility reports.

    Parameters:
    site_folder (str): The path to the subdirectory to be scanned.

    Process:
    1. Retrieves the domain ID for the folder by calling `get_site_id_by_domain_name`.
    2. If a valid domain ID is found, calls the `scan_pdfs` function, passing the path to the folder and the domain ID as arguments.
    """
    # get last folder in site folders


    domain_id = get_site_id_by_domain_name(os.path.basename(site_folder))

    if domain_id is not None:
        scan_pdfs(site_folder, domain_id)


