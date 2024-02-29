import json
import re

import requests
from bs4 import BeautifulSoup
import re



def get_box_contents(box_url):

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

                try:
                    json_dict = json.loads(raw_string_dict)
                    for item in json_dict['items']:
                        if item['extension'] == "pdf":
                            print(item)
                            print(item['name'])
                            return box_url



                except json.decoder.JSONDecodeError:
                    raw_string_dict = raw_string_dict + "}"
                    json_dict = json.loads(raw_string_dict)



temp_pdf_path = "C:\\Users\\913678186\\IdeaProjects\\sf_state_pdf_website_scan\\temp\\temp.pdf"
def download_from_box(box_link):

    if not box_share_pattern_match(box_link):
        print("Not a valid box share link")
        return False


    direct_download_url = "https://sfsu.app.box.com/public/static/{share_hash}.{extension}"
    share_hash = box_link.split("/")[-1]
    if get_box_contents(box_link):
        print("Found PDF")


        download_url = direct_download_url.format(share_hash=share_hash, extension=".pdf")
        file = requests.get(download_url, stream=True)
        with open(temp_pdf_path, "wb") as f:
            f.write(file.content)
        return True
def box_share_pattern_match(url):
    # Pattern to match the specific domain and extract the hash
    pattern = r'https?://sfsu\.box\.com/s/([a-zA-Z0-9]{32})$'
    match = re.match(pattern, url)

    if match:
        # If the pattern matches, return the hash
        return True
    else:
        # If the pattern does not match, return None or an appropriate message
        return False


# download_from_box(test)
