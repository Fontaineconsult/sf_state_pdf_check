import win32com.client as win32
import pythoncom
import time

from communications import build_emails

emails = build_emails()


def generate_email(html_content, reciever):
    print("html_content", html_content)
    try:
        # Ensure Outlook is correctly registered and accessible via COM
        pythoncom.CoInitialize()

        print("1. Attempting to create Outlook application instance...")
        outlook = win32.Dispatch('Outlook.Application')
        print("Outlook application instance created.")

        # Get the MAPI namespace
        print("2. Getting MAPI namespace...")
        namespace = outlook.GetNamespace("MAPI")
        print("MAPI namespace obtained.")

        # Wait for a short period to ensure everything is initialized
        time.sleep(2)

        # Create a new mail item
        print("3. Creating new mail item...")
        mail = outlook.CreateItem(0)  # 0: olMailItem
        print("Mail item created.")

        # Set the email properties
        mail.Subject = "Drupal PDF Accessibility Conformance Project"
        mail.BodyFormat = 2  # 2: olFormatHTML
        mail.HTMLBody = f"{html_content}"
        mail.To = "fontaine@sfsu.edu"
        print("Email properties set.")

        # Save the email as an MSG file
        save_path = r"C:\Users\913678186\IdeaProjects\sf_state_pdf_website_scan\emails\email.msg"  # Ensure the path includes the filename and extension
        mail.SaveAs(save_path, 3)  # 3: olMSG
        mail.send()
        print(f"Email saved as: {save_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pythoncom.CoUninitialize()


for email in emails:
    generate_email(email[0], email[1])