#!/usr/bin/env python3
import os

def delete_scans_files(root_folder):
    # Walk through the directory tree
    for current_path, dirs, files in os.walk(root_folder):
        for file in files:
            # Check if the file name contains the substring
            if "_scans.xlsx" in file:
                file_path = os.path.join(current_path, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    # Specify your main folder path here, or ask the user for input
    delete_scans_files(r"C:\Users\913678186\Box\ATI\PDF Accessibility\SF State Website PDF Scans")
