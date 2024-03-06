import json
import re

import requests
from bs4 import BeautifulSoup
import re

from data_import import add_pdf_report_failure


def get_box_contents(box_url, loc, domain_id):
    page_request = requests.get(box_url)

    if not page_request.ok:
        add_pdf_report_failure(box_url, loc, domain_id, f"Couldn't download {page_request.status_code}")
        return False, ""

    page_request = requests.get(box_url)

    if page_request:
        page_html = BeautifulSoup(page_request.content, features="lxml")

        page_scripts = page_html.find_all("script")
        expression = re.compile("Box\.postStreamData")
        items_expression = re.compile('"items":\[\{.*.}]')
        print(page_scripts)
        for script in page_scripts:
            if expression.search(script.text):

                clean_text = script.text.replace("'","")

                items = items_expression.search(clean_text)

                raw_string_dict = f"{{{items.group()}}}"


                json_dict = json.loads(raw_string_dict)
                for item in json_dict['items']:
                    if item['extension'] == "pdf":

                        if item["canDownload"] == False:
                            print("Box File is not downloadable")
                            return False, "Box File is not downloadable"

                        print(item)
                        print(item['name'])
                        return True, box_url





temp_pdf_path = "C:\\Users\\913678186\\IdeaProjects\\sf_state_pdf_website_scan\\temp\\temp.pdf"
def download_from_box(box_link, loc, domain_id):

    if not box_share_pattern_match(box_link):
        print("Not a valid box share link")
        return False, "Not a valid box share link"


    direct_download_url = "https://sfsu.app.box.com/public/static/{share_hash}.{extension}"
    share_hash = box_link.split("/")[-1]
    box_contents = get_box_contents(box_link, loc, domain_id)
    print(box_contents, box_link)
    if box_contents[0]:
        print("Found PDF")


        download_url = direct_download_url.format(share_hash=share_hash, extension="pdf")
        file = requests.get(download_url, stream=True)
        with open(temp_pdf_path, "wb") as f:
            f.write(file.content)
        return True, ""
    else:
        return False, box_contents[1]


def box_share_pattern_match(url):
    # Pattern to match the specific domain and extract the hash
    pattern = r'https:\/\/[a-zA-Z0-9.-]*\.box\.com\/s\/[a-zA-Z0-9]+'
    match = re.match(pattern, url)

    if match:
        # If the pattern matches, return the hash
        return True
    else:
        # If the pattern does not match, return None or an appropriate message
        return False
