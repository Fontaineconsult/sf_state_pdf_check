import os

from conformance_checker import full_pdf_scan
from data_export import get_pdfs_by_site_name, get_all_sites, write_data_to_excel, get_site_failures
from filters import check_for_node, is_high_priority

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




def count_reportable_pdfs():
    total_pdfs = 0
    all_sites = get_all_sites()

    for site in all_sites:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdfs_by_site_name(site)
        fail_data = get_site_failures(site)

        for item in site_data:
            item_list = list(item)
            print(item_list[1])
            if not check_for_node(item_list[1]):
                total_pdfs += 1

    return total_pdfs


def count_high_priority_pdfs():
    is_high_priority_count = 0

    all_sites = get_all_sites()
    for site in all_sites:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdfs_by_site_name(site)
        fail_data = get_site_failures(site)
        for item in site_data:

            if not is_high_priority(item):
                is_high_priority_count += 1
    return is_high_priority_count

def create_all_pdf_reports():
    full_pdf_scan(pdf_sites_folder)


build_all_xcel_reports()