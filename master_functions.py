import os

from conformance_checker import full_pdf_scan
from data_export import get_pdfs_by_site_name, get_all_sites, write_data_to_excel, get_site_failures

pdf_sites_folder = "C:\\Users\\913678186\\Box\\ATI\\PDF Accessibility\\SF State Website PDF Scans"
scans_output = "C:\\Users\\913678186\\Box\\ATI\\PDF Accessibility\\SF State Website PDF Scans\\{}"


def build_all_xcel_reports():

    all_sites = get_all_sites()

    for site in all_sites:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdfs_by_site_name(site)
        fail_data = get_site_failures(site)

        # check if scans folder exists and if not create it
        if not os.path.exists(scans_output.format(site_folder_name)):
            os.makedirs(scans_output.format(site_folder_name))

        write_data_to_excel(site_data, fail_data, scans_output.format(site_folder_name + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans.xlsx"))


def scan_all_sites():
    pass


def create_all_pdf_reports():
    full_pdf_scan(pdf_sites_folder)

build_all_xcel_reports()