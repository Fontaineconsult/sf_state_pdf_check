import re

node_check = re.compile(r".*./node/.*")
index_check = re.compile(r".*./index.php/.*")

def check_for_node(parent_uri):
    return True if (node_check.match(parent_uri) or index_check.match(parent_uri)) is not None else False



def is_high_priority(data):

    data = dict(data._asdict())

    if data['tagged'] == 0:
        return True
    if data['pdf_text_type'] == 'Image Only':
        return True
    if round(int(data['failed_checks']) / int(data['page_count'])) > 20:
        return True
    if data['has_form'] == 1 and round(int(data['failed_checks']) / int(data['page_count'])) > 3:
        return True
    return False
