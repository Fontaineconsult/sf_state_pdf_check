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
from sf_state_pdf_scan.run_spider_by_name import run_spider_by_name

# Import PDF report function
from master_functions import create_all_pdf_reports, create_single_pdf_report
from set_env import get_project_path

# Import HTML report function
from html_report import main as generate_html_report

# Import spider generation function
from sites import generate_spiders, generate_single_spider

# Import single site add function
from data_import import add_single_site

# Import archive update function
from update_archived import update_archives, update_archives_for_domain

# Import 404 status check function
from scan_refresh import refresh_status

COMPLETED_SPIDERS_FILE = 'sf_state_pdf_scan/sf_state_pdf_scan/completed_spiders.txt'
COMPLETED_CONFORMANCE_FILE = get_project_path('completed_conformance')


def clear_completed_spiders():
    """Clear the completed spiders file."""
    completed_file = Path(__file__).parent / COMPLETED_SPIDERS_FILE
    if completed_file.exists():
        completed_file.write_text('')
        print(f"Cleared completed spiders file: {completed_file}")


def clear_completed_conformance():
    """Clear the completed conformance scans file."""
    if COMPLETED_CONFORMANCE_FILE and os.path.exists(COMPLETED_CONFORMANCE_FILE):
        with open(COMPLETED_CONFORMANCE_FILE, 'w') as f:
            f.write('')
        print(f"Cleared completed conformance file: {COMPLETED_CONFORMANCE_FILE}")


def get_conformance_progress():
    """Get the count of completed conformance scans."""
    if COMPLETED_CONFORMANCE_FILE and os.path.exists(COMPLETED_CONFORMANCE_FILE):
        with open(COMPLETED_CONFORMANCE_FILE, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    return 0


def run_spiders():
    """Run the web spiders."""
    original_dir = os.getcwd()
    spider_dir = Path(__file__).parent / 'sf_state_pdf_scan'

    # Set Scrapy settings module environment variable - use full path from root
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'sf_state_pdf_scan.sf_state_pdf_scan.settings'

    os.chdir(spider_dir)

    run_all_spiders()
    os.chdir(original_dir)
    clear_completed_spiders()
    return True


def run_single_spider(spider_name):
    """Run a single spider by name."""
    original_dir = os.getcwd()
    spider_dir = Path(__file__).parent / 'sf_state_pdf_scan'

    # Set Scrapy settings module environment variable
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'sf_state_pdf_scan.sf_state_pdf_scan.settings'

    os.chdir(spider_dir)

    print(f"Running spider: {spider_name}")
    run_spider_by_name(spider_name)
    os.chdir(original_dir)
    return True


def run_pdf_reports():
    """Run PDF accessibility verification."""
    create_all_pdf_reports()
    clear_completed_conformance()  # Clear tracking after successful run
    return True


def run_single_pdf_report(domain):
    """Run PDF accessibility verification for a single domain."""
    create_single_pdf_report(domain)
    return True


def run_html_report(month=None):
    """Generate HTML accessibility report.

    Args:
        month: Optional month string to use in the report (e.g., 'January 2025').
    """
    generate_html_report(scan_month=month)
    return True


def run_generate_spiders():
    """Generate spider files for all sites."""
    generate_spiders()
    return True


def run_update_archives():
    """Update archived status for all PDFs in the database."""
    print("\nUpdating archived status for PDFs...")
    update_archives()
    return True


def run_update_archives_domain(domain_name):
    """Update archived status for PDFs from a specific domain."""
    print(f"\nUpdating archived status for domain: {domain_name}")
    update_archives_for_domain(domain_name)
    return True


def run_check_404():
    """Check 404 status for all PDFs and parent URLs."""
    print("\nChecking 404 status for all PDFs...")
    refresh_status()
    return True


def run_check_404_site(domain):
    """Check 404 status for PDFs from a specific domain."""
    print(f"\nChecking 404 status for domain: {domain}")
    refresh_status(site=domain)
    return True


def run_check_404_box_only():
    """Check 404 status for Box links only."""
    print("\nChecking 404 status for Box links only...")
    refresh_status(box_only=True)
    return True


def run_add_site(domain_name, box_folder=None):
    """Add a new site: database record and spider."""
    print(f"\n=== Adding Site: {domain_name} ===\n")

    # Validate domain format
    domain_name = domain_name.strip().lower()
    if domain_name.startswith('http'):
        domain_name = domain_name.split('://')[-1].rstrip('/')
    if domain_name.startswith('www.'):
        domain_name = domain_name[4:]

    if not domain_name.endswith('.sfsu.edu'):
        print(f"Error: Domain must be an sfsu.edu subdomain (got: {domain_name})")
        return False

    # Step 1: Add to database
    print("Step 1/2: Adding to database...")
    db_success, db_message, site_id = add_single_site(domain_name, box_folder)
    print(f"  {db_message}")
    if box_folder:
        print(f"  Box folder: {box_folder}")
    if not db_success and "already exists" not in db_message:
        return False

    # Step 2: Generate spider
    print("\nStep 2/2: Generating spider...")
    spider_success, spider_message = generate_single_spider(domain_name)
    print(f"  {spider_message}")

    print(f"\n=== Site '{domain_name}' setup complete! ===")
    return True


def run_full_cycle():
    """Run a complete cycle of all three components."""
    print("\n=== Starting Full Cycle ===")

    # Run spiders
    print("\nPhase 1: Running web spiders...")
    spider_success = run_spiders()

    # Run PDF reports
    print("\nPhase 2: Running PDF accessibility verification...")
    pdf_success = run_pdf_reports()

    # Run HTML report
    print("\nPhase 3: Generating HTML report...")
    html_success = run_html_report()

    print("\n=== Cycle Complete ===")
    return spider_success and pdf_success and html_success


def run_loop():
    """Run all components in a continuous loop."""
    import time

    cycle_count = 0
    loop_delay = 3600  # 1 hour between cycles

    print("Starting continuous loop mode")
    print(f"Delay between cycles: {loop_delay} seconds ({loop_delay/3600} hours)")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            cycle_count += 1
            print(f"\n{'='*60}")
            print(f"CYCLE #{cycle_count}")
            print(f"{'='*60}")

            run_full_cycle()

            print(f"\nWaiting {loop_delay} seconds until next cycle...")
            print(f"Next cycle starts at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + loop_delay))}")
            time.sleep(loop_delay)

    except KeyboardInterrupt:
        print(f"\n\nLoop stopped by user")
        print(f"Total cycles completed: {cycle_count}")
        return


def main():
    parser = argparse.ArgumentParser(description='SF State PDF Scanner')
    parser.add_argument('--generate-spiders', action='store_true', help='Generate spider files for all sites')
    parser.add_argument('--spiders', action='store_true', help='Run web spiders')
    parser.add_argument('--spider', type=str, metavar='NAME', help='Run a single spider by name')
    parser.add_argument('--pdf-reports', action='store_true', help='Run PDF accessibility verification for all sites')
    parser.add_argument('--pdf-report', type=str, metavar='DOMAIN', help='Run PDF accessibility verification for a single domain (e.g., access.sfsu.edu)')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML accessibility report')
    parser.add_argument('--month', type=str, metavar='MONTH', help='Month to use in HTML report (e.g., "January 2025")')
    parser.add_argument('--cycle', action='store_true', help='Run one full cycle of all components')
    parser.add_argument('--loop', action='store_true', help='Run continuous loop of all components')
    parser.add_argument('--clear-conformance', action='store_true', help='Clear the completed conformance scans tracking file')
    parser.add_argument('--conformance-progress', action='store_true', help='Show the number of completed conformance scans')
    parser.add_argument('--update-archives', action='store_true', help='Update archived status for all PDFs in the database')
    parser.add_argument('--update-archive', type=str, metavar='DOMAIN', help='Update archived status for a single domain (e.g., retire.sfsu.edu)')
    parser.add_argument('--check-404', action='store_true', help='Check 404 status for all PDFs and parent URLs')
    parser.add_argument('--check-404-site', type=str, metavar='DOMAIN', help='Check 404 status for a single domain (e.g., access.sfsu.edu)')
    parser.add_argument('--check-404-box', action='store_true', help='Check 404 status for Box links only')
    parser.add_argument('--add-site', type=str, metavar='DOMAIN',
                        help='Add a new site (e.g., newdomain.sfsu.edu)')
    parser.add_argument('--box-folder', type=str, metavar='URL',
                        help='Box folder URL for --add-site (e.g., https://sfsu.box.com/s/xxxxx)')

    args = parser.parse_args()

    if args.generate_spiders:
        run_generate_spiders()
    elif args.spiders:
        run_spiders()
    elif args.spider:
        run_single_spider(args.spider)
    elif args.pdf_reports:
        run_pdf_reports()
    elif args.pdf_report:
        run_single_pdf_report(args.pdf_report)
    elif args.html_report:
        run_html_report(month=args.month)
    elif args.cycle:
        run_full_cycle()
    elif args.loop:
        run_loop()
    elif args.clear_conformance:
        clear_completed_conformance()
    elif args.conformance_progress:
        count = get_conformance_progress()
        print(f"Completed conformance scans: {count}")
    elif args.update_archives:
        run_update_archives()
    elif args.update_archive:
        run_update_archives_domain(args.update_archive)
    elif args.check_404:
        run_check_404()
    elif args.check_404_site:
        run_check_404_site(args.check_404_site)
    elif args.check_404_box:
        run_check_404_box_only()
    elif args.add_site:
        run_add_site(args.add_site, box_folder=args.box_folder)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()