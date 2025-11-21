import os
from datetime import datetime

import sys
from pathlib import Path

# add this file's parent folder to sys.path
_parent_dir = str(Path(__file__).resolve().parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)


from conformance_checker import full_pdf_scan, refresh_existing_pdf_reports, single_site_pdf_scan
from data_export import get_pdf_reports_by_site_name, get_all_sites, write_data_to_excel, get_site_failures

from filters import check_for_node, is_high_priority
from scan_refresh import refresh_status
from tools import mark_pdfs_as_removed
from set_env import get_box_path
from update_archived import update_archives

pdf_sites_folder = get_box_path('pdf_scans')
scans_output = get_box_path('pdf_scans') + "\\{}"




def build_all_xcel_reports():

    all_sites = get_all_sites()

    for site in all_sites:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdf_reports_by_site_name(site)
        fail_data = get_site_failures(site)

        # check if scans folder exists and if not create it
        if not os.path.exists(scans_output.format(site_folder_name)):
            os.makedirs(scans_output.format(site_folder_name))

        write_data_to_excel(site_data, fail_data, scans_output.format(site_folder_name + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans.xlsx"))


def build_single_xcel_report(site_name):

        site_folder_name = site_name.replace(".", "-")
        site_data = get_pdf_reports_by_site_name(site_name)
        print(site_data)
        fail_data = get_site_failures(site_name)

        # check if scans folder exists and if not create it
        if not os.path.exists(scans_output.format(site_folder_name)):
            os.makedirs(scans_output.format(site_folder_name))

        #create a backup folder for xlxs file if it doesn't exist "backups"
        if not os.path.exists(scans_output.format(site_folder_name) + "\\" + "backups"):
            os.makedirs(scans_output.format(site_folder_name) + "\\" + "backups")

        # move the old file to the backup folder
        if os.path.exists(scans_output.format(site_folder_name + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans.xlsx")):
            os.rename(scans_output.format(site_folder_name + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans.xlsx"),
                      scans_output.format(site_folder_name) + "\\" + "backups" + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans-backup-{datetime.now().strftime('%Y-%m-%d')}.xlsx")

        write_data_to_excel(site_data, fail_data, scans_output.format(site_folder_name + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans.xlsx"))




def count_reportable_pdfs():
    total_pdfs = 0
    all_sites = get_all_sites()

    for site in all_sites:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdf_reports_by_site_name(site)
        fail_data = get_site_failures(site)

        for item in site_data:
            item_list = list(item)
            if not check_for_node(item_list[1]):
                total_pdfs += 1

    return total_pdfs

def count_high_priority_pdfs():
    is_high_priority_count = 0

    all_sites = get_all_sites()
    for site in all_sites:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdf_reports_by_site_name(site)
        fail_data = get_site_failures(site)
        for item in site_data:

            if not is_high_priority(item):
                is_high_priority_count += 1
    return is_high_priority_count

# def backup_database():
#
#     # copies drupal_pdfs.db from this folder to /database-backups and appends '-backup--YYYY-MM-DD' to the filename
#
#     import shutil
#     from datetime import datetime
#     db_backup_folder = "C:\\Users\\913678186\\Box\\ATI\\PDF Accessibility\\SF State Website PDF Scans\\database-backups"
#     if not os.path.exists(db_backup_folder):
#         os.makedirs(db_backup_folder)
#     db_file = "C:\\Users\\913678186\\Box\\ATI\\PDF Accessibility\\SF State Website PDF Scans\\drupal_pdfs.db"
#     if os.path.exists(db_file):
#


def create_all_pdf_reports():
    """
    Initiates a full PDF scan for all subdirectories within the specified folder.

    This function serves as the starting point for the PDF scan process. It performs the following steps:
    1. Calls the `full_pdf_scan` function, passing the path to the main directory containing subdirectories with PDF files to be scanned.
    2. The `full_pdf_scan` function iterates over each subdirectory within the specified folder.
    3. For each subdirectory, it retrieves the domain ID by calling the `get_site_id_by_domain_name` function.
    4. If a valid domain ID is found, it calls the `scan_pdfs` function, passing the path to the current subdirectory and the domain ID as arguments.
    5. The `scan_pdfs` function loads the list of PDF URLs and their locations from text files in the specified directory.
    6. For each PDF URL and location:
        a. Checks if an accessibility report already exists for the PDF by calling the `check_if_pdf_report_exists` function.
        b. If no report exists, downloads the PDF by calling the `download_pdf_into_memory` or `download_from_box` function.
        c. Generates an accessibility report using the `create_verapdf_report` function.
        d. Adds the report to the database by calling the `add_pdf_file_to_database` function if successful, or logs a failure by calling the `add_pdf_report_failure` function if not.

    Parameters:
    None

    Returns:
    None
    """

    print("Starting full PDF scan...")

    ##
    ## Make sure to back up the database before running this function
    ##
    # Import pdfs and test for accessibility
    full_pdf_scan(pdf_sites_folder)
    # remove 404s and set as 404
    refresh_status()
    # compare the pdfs in the folder to the database and mark as removed if not in the folder
    mark_pdfs_as_removed(pdf_sites_folder)
    # refresh_existing_pdf_reports
    refresh_existing_pdf_reports()
    # update archive status
    update_archives()


def single_site_full_refresh():
    single_site_pdf_scan(os.path.join(get_box_path('pdf_scans'), "access-sfsu-edu"))
    refresh_status(site="access.sfsu.edu")
    mark_pdfs_as_removed(pdf_sites_folder)
    refresh_existing_pdf_reports(single_domain="access.sfsu.edu")

if __name__=="__main__":
    create_all_pdf_reports()


# create_all_pdf_reports()
# build_all_xcel_reports()
# build_single_xcel_report("creativewriting.sfsu.edu")