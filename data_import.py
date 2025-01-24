import csv
import sqlite3


def add_employees_from_csv_file(file_path):
    # Define the connection and cursor
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    # Open the CSV file and iterate over its rows
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            # if row is blank or empty string, skip it
            if not row or row[1] == '':
                continue
            # Prepare last name (assuming the full name is in row[0] and employee_id is in row[1])
            full_name = row[0].split(" ")
            first_name = full_name[0]
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""
            # Insert each row into the database only if employee_id is unique
            cursor.execute("INSERT OR IGNORE INTO site_user (employee_id, first_name, last_name, email)"
                           " VALUES (?, ?, ?, ?)", (row[1], first_name, last_name, row[2]))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def update_managers_boolean_in_site_user_table(csv_file_path):
    # load managers id numbers from csv file
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        managers = [row[0] for row in csv_reader]

    # Define the connection and cursor
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    for employee_id in managers:
        # Update the is_manager column in the site_user table
        # Use 1 to represent True for the is_manager BOOLEAN column in SQLite
        cursor.execute("UPDATE site_user SET is_manager = 1 WHERE employee_id = ?", (employee_id,))

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()

    print("Managers updated successfully.")


def add_sites_from_site_csv_file(file_path):
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    # open csv file
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)

    # print each line in csv reader
        for row in csv_reader:

            for site in row[0].split(","):

                domain_name = site.replace("www.", "", 1)
                security_group_name = row[1]
                cursor.execute("INSERT INTO drupal_site (domain_name, security_group_name) VALUES (?, ?)", (domain_name, security_group_name))
                conn.commit()
    cursor.close()



def add_employee_and_site_assignments_from_csv_file(file_path):
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            sec_group = row[0]
            employee_name = row[1]
            employee_id = row[2]
            employee_email = row[3]

            full_name = employee_name.split(" ")
            first_name = full_name[0]
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""

            # check and insert employee into site_user table if they don't exist, if they do exist return the record
            cursor.execute("INSERT OR IGNORE INTO site_user (employee_id, first_name, last_name, email) VALUES (?, ?, ?, ?)", (employee_id, first_name, last_name, employee_email))

            # get employee record by employee id
            employee = cursor.execute("SELECT * FROM site_user WHERE employee_id = ?", (employee_id,)).fetchone()

            # get site record by security group name
            site = cursor.execute("SELECT * FROM drupal_site WHERE security_group_name = ?", (sec_group,)).fetchone()

            if site is None or employee is None:
                print("Site or employee not found in the database.")
                continue


            # insert employee and site assignment into site_assignment table
            cursor.execute("INSERT INTO site_assignment (site_id, user_id) VALUES (?, ?)", (site[0], employee[0]))

            conn.commit()
        conn.close()


def add_admin_contacts(file_path):
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:


            site = row[0]
            employee_name = row[2]
            employee_email = row[3]
            if site is None or employee_name is None:
                conn
            generated_id = f"{hash(employee_email) % 1000000000}"

            # print(site,employee_name,employee_email, generated_id)

            full_name = employee_name.split(" ")
            first_name = full_name[0]
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""

            print(full_name, first_name,last_name, generated_id, employee_email)

            # Check if email already exists in the site_user table
            email_exists = cursor.execute("SELECT * FROM site_user WHERE email = ?", (employee_email,)).fetchone()
            if email_exists:
                # cursor.execute("UPDATE site_user SET is_manager = 1 WHERE email = ?", (employee_email,))
                print("email_exists", email_exists)

                assignment_exists = cursor.execute("SELECT * FROM site_assignment WHERE domain_name = ? AND user_id = ?", (site, email_exists[0]))
                if not assignment_exists:
                    cursor.execute("INSERT INTO site_assignment (domain_name, user_id) VALUES (?, ?)", (site, email_exists[0]))

            if not email_exists:
                cursor.execute("INSERT INTO site_user (employee_id, first_name, last_name, email) VALUES (?, ?, ?, ?)", (generated_id, first_name, last_name, employee_email))
                employee = cursor.execute("SELECT * FROM site_user WHERE email = ?", (employee_email,)).fetchone()
                cursor.execute("INSERT INTO site_assignment (domain_name, user_id) VALUES (?, ?)", (site, employee[0]))

        #     #check and insert employee into site_user table if they don't exist, if they do exist return the record
        #     cursor.execute("INSERT OR IGNORE INTO site_user (employee_id, first_name, last_name, email) VALUES (?, ?, ?, ?)", (generated_id, first_name, last_name, employee_email))
        #
        #     # get employee record by employee id
        #     employee = cursor.execute("SELECT * FROM site_user WHERE employee_id = ?", (employee_id,)).fetchone()
        #
        #     # get site record by security group name
        #     site = cursor.execute("SELECT * FROM drupal_site WHERE security_group_name = ?", (sec_group,)).fetchone()
        #
        #
        #
            if site is None or employee is None:
                print("Site or employee not found in the database.")
                continue
        #
        #
        #     # insert employee and site assignment into site_assignment table
        #     cursor.execute("INSERT INTO site_assignment (site_id, user_id) VALUES (?, ?)", (site[0], employee[0]))
        #
        #     conn.commit()
        # conn.close()


add_admin_contacts(r"C:\Users\913678186\IdeaProjects\sf_state_pdf_website_scan\admin_contacts.csv")

def check_if_pdf_file_exists(pdf_uri, parent_uri, drupal_site_id, pdf_hash):

    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    exists = cursor.execute("SELECT * FROM drupal_pdf_files WHERE pdf_uri = ? AND parent_uri = ? AND drupal_site_id = ? AND file_hash = ?",
                   (pdf_uri, parent_uri, drupal_site_id, pdf_hash)).fetchone()

    conn.close()

    return True if exists else False


def get_site_id_from_domain_name(domain_name):
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    site_id = cursor.execute("SELECT id FROM drupal_site WHERE domain_name = ?", (domain_name,)).fetchone()
    conn.close()
    return site_id[0] if site_id else None


def add_pdf_file_to_database(pdf_uri, parent_uri, drupal_site_id, violation_dict):
    # Define the connection and cursor
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()

    # Assuming violation_dict contains keys for violations, failed_checks, tagged, etc.
    violations = violation_dict.get("violations", 0)
    failed_checks = violation_dict.get("failed_checks", 0)
    tagged = violation_dict.get("tagged", True)
    check_for_image_only = violation_dict.get("check_for_image_only", False)
    pdf_text_type = violation_dict.get("pdf_text_type", "")
    title_set = violation_dict.get("metadata").get("title", None)
    language_set = violation_dict.get("metadata").get("language", None)
    page_count = violation_dict.get("doc_data").get("pages", 0)
    file_hash = violation_dict.get("file_hash", "")
    has_form = violation_dict.get("has_form", False)


    # check if pdf report exsits by file has
    exists = cursor.execute("SELECT * FROM pdf_report WHERE pdf_hash = ?", (file_hash,)).fetchone()

    if not exists:

        cursor.execute("""
        INSERT INTO pdf_report (
            violations,
            failed_checks,
            tagged,
            check_for_image_only,
            pdf_text_type,
            title_set,
            language_set,
            page_count,
            pdf_hash,
            has_form
        ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            violations,
            failed_checks,
            tagged,
            check_for_image_only,
            pdf_text_type,
            title_set,
            language_set,
            page_count,
            file_hash,
            has_form
        ))
        conn.commit()
    else:
        print("PDF report already exists in the database.")


    # check if pdf exists by pdf_uri, parent_uri, and file_hash
    exists = cursor.execute("SELECT * FROM drupal_pdf_files WHERE pdf_uri = ? AND parent_uri = ? AND file_hash = ?",
                   (pdf_uri, parent_uri, file_hash)).fetchone()


    if exists:
        print("PDF file already exists in the database.")

    if not exists:

        # Insert a new row into the drupal_pdf_files table
        cursor.execute("""
        INSERT INTO drupal_pdf_files (
            pdf_uri,
            parent_uri,
            drupal_site_id,
            file_hash
        ) VALUES (?, ?, ?, ?)
        """, (
            pdf_uri,
            parent_uri,
            drupal_site_id,
            file_hash
        ))

        # Commit the changes and close the connection
        conn.commit()
    conn.close()



def get_all_sites_domain_names():
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    sites = cursor.execute("SELECT domain_name FROM drupal_site").fetchall()
    conn.close()

    return [site[0] for site in sites]


def get_site_id_by_domain_name(domain_name):

    domain_name = domain_name.replace("-",".")

    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    site_id = cursor.execute("SELECT id FROM drupal_site WHERE domain_name = ?", (domain_name,)).fetchone()
    conn.close()
    return site_id[0] if site_id else None




def check_if_pdf_report_exists(pdf_uri, parent_uri):

    # first check if a pdf exists with the pdf_uri and parent_uri
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    pdf_file = cursor.execute("SELECT * FROM drupal_pdf_files WHERE pdf_uri = ? AND parent_uri = ?", (pdf_uri, parent_uri)).fetchone()



    if pdf_file:
        # if a pdf exists, check if a report exists for the pdf
        pdf_hash = pdf_file[5]
        report = cursor.execute("SELECT * FROM pdf_report WHERE pdf_hash = ?", (pdf_hash,)).fetchone()
        if report:
            conn.close()
            return True
    conn.close()
    return False


def add_pdf_report_failure(pdf_uri, parent_uri, site_id, error_message):

        conn = sqlite3.connect('drupal_pdfs.db')
        cursor = conn.cursor()

        # get pdf_id from pdf table with pdf_uri and parent_uri
        print(pdf_uri, parent_uri, site_id, error_message)

        pdf_id = cursor.execute("SELECT * FROM drupal_pdf_files WHERE pdf_uri = ? AND parent_uri = ?", (pdf_uri, parent_uri)).fetchone()
        print(pdf_id)
        if pdf_id:
            pdf_id = pdf_id[0]

            # add record to failure table
            cursor.execute("INSERT INTO failure (site_id, pdf_id, error_message) VALUES (?, ?, ?)", (site_id, pdf_id, error_message))
            conn.commit()
            conn.close()
        else:
            cursor.execute("INSERT INTO failure (site_id, pdf_uri, error_message) VALUES (?, ?, ?)", (site_id, pdf_uri, error_message))
            conn.commit()
            conn.close()
            print("No PDF in system add raw failure")


def truncate_reports_table():
    conn = sqlite3.connect('drupal_pdfs.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pdf_report")
    cursor.execute("DELETE FROM failure")
    conn.commit()
    conn.close()





def import_box_folders():


    conn = sqlite3.connect("drupal_pdfs.db")
    cursor = conn.cursor()

    sql = '''
    UPDATE drupal_site
    SET box_folder = ?
    WHERE domain_name = ?;
    '''

    with open(r"box_folders.csv", "r", encoding='utf-8') as f:
        csvreader = csv.reader(f)
        next(csvreader, None)

        for item in csvreader:
            cursor.execute(sql, (item[1], item[0]))

    conn.commit()
    conn.close()

