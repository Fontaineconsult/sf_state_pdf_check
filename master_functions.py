from data_export import get_pdfs_by_site_name, get_all_sites, write_data_to_excel


scans_output = "C:\\Users\\913678186\\Box\\ATI\\PDF Accessibility\\SF State Website PDF Scans\\{}"


def build_all_xcel_reports():

    data = get_all_sites()

    for site in data:
        site_folder_name = site.replace(".", "-")
        site_data = get_pdfs_by_site_name(site)
        write_data_to_excel(site_data, scans_output.format(site_folder_name + "\\" + f"{site_folder_name.split('-')[0]}-pdf-scans.xlsx"))

