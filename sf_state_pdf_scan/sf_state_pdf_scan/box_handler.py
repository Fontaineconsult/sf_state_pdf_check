import json
import re

import requests
from bs4 import BeautifulSoup

direct_download_url = "https://sfsu.app.box.com/public/static/{share_hash}.{extension}"


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
                            return box_url
                        print(item)
                        print(item['name'])
                        print(direct_download_url.format())

                except json.decoder.JSONDecodeError:
                    raw_string_dict = raw_string_dict + "}"
                    json_dict = json.loads(raw_string_dict)


