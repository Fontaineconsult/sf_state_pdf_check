import sqlite3
from collections import namedtuple
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.table import Table, TableStyleInfo



def get_all_sites():

    with open("get_all_sites.sql", 'r') as file:
        sql_query = file.read()
        conn = sqlite3.connect("drupal_pdfs.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        results = [result[0] for result in results]

        if not results:
            return []
        return results



def get_pdfs_by_site_name(site_name):

    with open("get_pdf_reports_by_site_name.sql", 'r') as file:
        sql_query = file.read()
        formatted_query = sql_query.format(site_name=site_name)
        print(formatted_query)

        conn = sqlite3.connect("drupal_pdfs.db")
        cursor = conn.cursor()

        # Execute the SQL query
        cursor.execute(formatted_query)
        results = cursor.fetchall()

        # If there are no results, return an empty list
        if not results:
            return []

        # Get column names from the cursor
        col_names = [desc[0] for desc in cursor.description]
        # Create a namedtuple class with column names
        Row = namedtuple('Row', col_names)

        # Convert sqlite3.Row objects to namedtuples
        results = [Row(*row) for row in results]

        # Close the database connection
        conn.close()

        return results


from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font




def write_data_to_excel(data, file_name="output.xlsx"):
    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    if not data:
        print("No data to write to Excel.")
        return

    # Assuming all namedtuples have the same fields, get column names from the first item
    columns = list(data[0]._fields)

    columns.append("Errors/Page")

    # Write the column headers
    ws.append(columns)

    # Write the data rows
    for row, item in enumerate(data, start=2):  # Start from row 2 to account for the header
        # Convert named tuple to a list to edit its values
        item_list = list(item)
        item_list[3] = item_list[3][0:6]
        item_list[2] = item_list[2].split(" ")[0]

        item_list[9] = "Yes" if item_list[9] == 1 else "No"
        item_list[10] = "Yes" if item_list[10] == 1 else "No"
        item_list[12] = "Yes" if item_list[12] == 1 else "No"
        item_list[13] = "Yes" if item_list[13] == 1 else "No"
        item_list.append(round(int(item[8]) / int(item[14])) if item[8] != 0 else 0)

        # Modify the URL fields directly with HYPERLINK formula
        item_list[0] = f'=HYPERLINK("{item[0]}", "{item[0]}")'
        item_list[1] = f'=HYPERLINK("{item[1]}", "{item[1]}")'

        # Append the modified list of values to the worksheet
        ws.append(item_list)



    # Apply font styles for hyperlink columns
    for row in range(2, len(data) + 2):  # Adjusting range to account for header row
        for col in ['A', 'B']:  # Assuming hyperlinks are in columns A and B
            cell = ws[f'{col}{row}']
            cell.font = Font(color='0563C1', underline='single')

    # Determine the Excel table range
    table_range = f"A1:{chr(64 + len(columns))}{len(data) + 1}"

    # Create a table
    table = Table(displayName="DataTable", ref=table_range)

    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    table.tableStyleInfo = style

    # Add the table to the worksheet
    ws.add_table(table)

    # Save the Excel file
    wb.save(file_name)
    print(f"Data written to {file_name} with a table format.")



