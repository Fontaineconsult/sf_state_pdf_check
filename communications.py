import sqlite3
from collections import namedtuple

from filters import is_high_priority


def generate_pdf_count_by_employee(employee_id):
    user_table = {}
    # use the get_pdfs_by_user_id.sql to get users pdfs
    with open('sql/get_pdfs_by_user_id.sql', 'r') as file:
        sql_query = file.read()
        formatted_query = sql_query.format(employee_id=employee_id)
        conn = sqlite3.connect("drupal_pdfs.db")
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(formatted_query)
        results = cursor.fetchall()
        domains = list(set([item[4] for item in results]))

    with open('sql/get_pdf_reports_by_site_name.sql') as pdf_reports_sql:
        sql_query = pdf_reports_sql.read()
        conn = sqlite3.connect("drupal_pdfs.db")
        cursor = conn.cursor()

        for domain in domains:
            formatted_query = sql_query.format(site_name=domain)
            cursor.execute(formatted_query)
            results = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]

            Row = namedtuple('Row', col_names)


            results = [Row(*row) for row in results]
            user_table[domain] = {"priority": 0, "total": 0, "box_folder": ""}
            for item in results:
                user_table[domain]["total"] += 1
                user_table[domain]["box_folder"] = item.box_folder
                if is_high_priority(item):
                    user_table[domain]["priority"] += 1

    return user_table


def create_html_email_grid(data):
    # Starting the HTML
    html_grid = '''
    <table style="width: 600px; border-collapse: collapse;">
        <tbody>
    '''
    # Convert dictionary to list of items for easier slicing
    items = list(data.items())

    # Determine number of items per row based on the total number of items
    if len(items) == 1:
        html_grid = '''
        <table style="width: 200px; border-collapse: collapse;">
            <tbody>
        '''
        items_per_row = 1
        col_width = "100%"
    elif len(items) == 2:
        html_grid = '''
        <table style="width: 400px; border-collapse: collapse;">
            <tbody>
        '''
        items_per_row = 2
        col_width = "50%"
    else:
        items_per_row = 3
        col_width = "33.33%"

    # Adding rows of data to the HTML grid
    for i in range(0, len(items), items_per_row):
        html_grid += '<tr>'
        row_items = items[i:i + items_per_row]
        for site, details in row_items:
            html_grid += f'''
                <td style="border: 1px solid #dddddd; padding: 4px; width: {col_width}; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">
                    <a href="{details['box_folder']}" style="text-decoration: none;">{site}</a>
                    <div><b>{details["total"]}</b> PDFs | <span style="color: #8B0000;"><b>{details["priority"]}</b> Need Attention</span></div>
                </td>
            '''
        # Fill remaining cells in the row if there are fewer than the number of items per row
        for _ in range(items_per_row - len(row_items)):
            html_grid += f'''
                <td style="border: 1px solid #dddddd; padding: 4px; width: {col_width}; background-color: #D3D3D3;">
                    <!-- Empty cell -->
                </td>
            '''
        html_grid += '</tr>'

    # Ending the HTML
    html_grid += '</tbody></table>'
    return html_grid




def template_email(data_dict):

    with open(r"C:\Users\913678186\Box\ATI\PDF Accessibility\Reports\build_files\email_template.html", "r") as file:
        email_template = file.read()
        formatted_template = email_template.format(**data_dict)
        return formatted_template



def build_emails():


    with open('sql/get_all_users_with_pdf_files.sql') as pdf_reports_sql:
        sql_query = pdf_reports_sql.read()
        conn = sqlite3.connect("drupal_pdfs.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        for employee in results:
            print(employee)

            html_table = create_html_email_grid(generate_pdf_count_by_employee(employee[3]))

            template_values = {
                "employee_first_name": employee[0],
                "employee_full_name": f"{employee[0]} {employee[1]}",
                "pdf_data_table": html_table
            }
            email_text = template_email(template_values)
            print(email_text)

build_emails()


# template_email("ds")

# print(create_html_email_grid(generate_pdf_count_by_employee("912793588")))