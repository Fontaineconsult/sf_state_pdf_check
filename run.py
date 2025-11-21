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

# Import spider generation function
from sites import generate_spiders

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

    # Set Scrapy settings module environment variable - use full path from root
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'sf_state_pdf_scan.sf_state_pdf_scan.settings'

    os.chdir(spider_dir)

    run_all_spiders()
    os.chdir(original_dir)
    clear_completed_spiders()
    return True


def run_pdf_reports():
    """Run PDF accessibility verification."""
    create_all_pdf_reports()
    return True


def run_html_report():
    """Generate HTML accessibility report."""
    generate_html_report()
    return True


def run_generate_spiders():
    """Generate spider files for all sites."""
    generate_spiders()
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
    parser.add_argument('--pdf-reports', action='store_true', help='Run PDF accessibility verification')
    parser.add_argument('--html-report', action='store_true', help='Generate HTML accessibility report')
    parser.add_argument('--cycle', action='store_true', help='Run one full cycle of all components')
    parser.add_argument('--loop', action='store_true', help='Run continuous loop of all components')

    args = parser.parse_args()

    if args.generate_spiders:
        run_generate_spiders()
    elif args.spiders:
        run_spiders()
    elif args.pdf_reports:
        run_pdf_reports()
    elif args.html_report:
        run_html_report()
    elif args.cycle:
        run_full_cycle()
    elif args.loop:
        run_loop()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()