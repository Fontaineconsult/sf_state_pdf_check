import os
import time
import requests
import subprocess

from data_import import add_pdf_file_to_database, get_site_id_by_domain_name
from pdf_priority import violation_counter, pdf_check, pdf_status


def download_pdf_into_memory(url):
    return requests.get(url).content



def create_verapdf_report(url):
    print(os.environ['PATH'])
    pdf_download = download_pdf_into_memory(url)

    temp_pdf_path = "C:\\Users\\913678186\\IdeaProjects\\sf_state_pdf_website_scan\\temp\\temp.pdf"
    temp_profile_path = "C:\\Users\\913678186\\IdeaProjects\\sf_state_pdf_website_scan\\temp\\temp_profile.json"




    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_download)

    try:
        verapdf_command = f'verapdf -f ua1 --format json "{temp_pdf_path}" > "{temp_profile_path}"'

        # Execute the command and capture the output
        try:
            subprocess.run(verapdf_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(e.output)

        violations = violation_counter(temp_profile_path)
        violations.update(pdf_check(temp_pdf_path))
        print(violations)
        return {"report": {"report": violations, "status": "Succeeded"}}
    except KeyError as e:
        return {"report": {"report": "", "status": "Failed"}}




def load_text_file_lines(file_path):
    with open(file_path) as f:
        return f.read().splitlines()


def loop_through_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):

                return load_text_file_lines(os.path.join(folder_path,file))


def scan_pdfs(directory, domain_id):
    pdf_locations = loop_through_files_in_folder(directory)


    for file in pdf_locations:
        file, loc = file.rstrip(" ").split(" ")
        report = create_verapdf_report(file)

        if report["report"]["status"] == "Succeeded":

            add_pdf_file_to_database(file, loc, domain_id, report["report"]["report"])



def full_pdf_scan(site_folders):
    print("f")
    # get all folders in the site_folders directory
    for folder in os.listdir(site_folders):
        domain_id = get_site_id_by_domain_name(folder)
        if domain_id is not None:

            print(os.path.join(site_folders, folder), domain_id)
            scan_pdfs(os.path.join(site_folders, folder), domain_id)




full_pdf_scan(r"C:\Users\913678186\Box\ATI\PDF Accessibility\SF State Website PDF Scans")