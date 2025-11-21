#!/usr/bin/env python3
"""
Simple runner for SF State PDF Check system.
"""

import argparse
import sys
import os
from pathlib import Path

# Fix import paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the spider runner function
from sf_state_pdf_scan.run_all_spiders import run_all_spiders

# Import PDF report function
from master_functions import create_all_pdf_reports

# Import HTML report function
from html_report import main as generate_html_report

COMPLETED_SPIDERS_FILE = 'sf_state_pdf_scan/sf_state_pdf_scan/completed_spiders.txt'


def clear_completed_spiders():
    """Clear the completed spiders file."""
    completed_file = Path(__file__).parent / COMPLETED_SPIDERS_FILE
    if completed_file.exists():
        completed_file.write_text('')
        print(f"Cleared completed spiders file: {completed_file}")


def run_spiders():
    """Run the web spiders."""
    original_dir = os.getcwd()
    spider_dir = Path(__file__).parent / 'sf_state_pdf_scan'
    os.chdir(spider_dir)

    try:
        run_all_spiders()
        # Only clear if spiders completed successfully
        os.chdir(original_dir)
        clear_completed_spiders()
        return True
    except SystemExit as e:
        # Check if it was a successful exit
        os.chdir(original_dir)
        if str(e) == '0' or str(e) == 'None':
            clear_completed_spiders()
        return True
    except Exception as e:
        print(f"Error running spiders: {e}")
        os.chdir(original_dir)
        return False


def run_pdf_reports():
    """Run PDF accessibility verification."""
    try:
        create_all_pdf_reports()
        return True
    except Exception as e:
        print(f"Error running PDF reports: {e}")
        return False


def run_html_report():
    """Generate HTML accessibility report."""
    try:
        generate_html_report()
        return True
    except Exception as e:
        print(f"Error generating HTML report: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='SF State PDF Scanner')
    parser.add_argument('--spiders', action='store_true', help='Run web spiders')
    parser.add_argument('--pdf-reports', action='store_true', help='Run PDF accessibility verification')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML accessibility report')

    args = parser.parse_args()

    if args.spiders:
        run_spiders()
    elif args.pdf_reports:
        run_pdf_reports()
    elif args.html_report:
        run_html_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()