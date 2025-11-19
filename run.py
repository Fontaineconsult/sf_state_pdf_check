#!/usr/bin/env python3
"""
Automated runner for SF State PDF Check system.
This script runs the web scraper and PDF report generation in a continuous loop.

Usage:
    python run.py

To stop the script:
    - Press Ctrl+C (keyboard interrupt)
    - Create a file named 'stop.signal' in the project directory
"""

import os
import sys
import time
import subprocess
import signal
from datetime import datetime
from pathlib import Path

# Import the master function for PDF report generation
from master_functions import create_all_pdf_reports

# Configuration
LOOP_DELAY = 3600  # Delay between runs in seconds (default: 1 hour)
STOP_SIGNAL_FILE = 'stop.signal'
SCRAPER_COMPLETED_FILE = 'sf_state_pdf_scan/sf_state_pdf_scan/completed_spiders.txt'


class AutomatedRunner:
    """Manages the automated execution of scraper and report generation."""

    def __init__(self):
        self.running = True
        self.project_root = Path(__file__).parent
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n[{self.get_timestamp()}] Received shutdown signal. Stopping after current operation...")
        self.running = False

    def get_timestamp(self):
        """Get current timestamp for logging."""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def check_stop_signal(self):
        """Check if stop signal file exists."""
        stop_file = self.project_root / STOP_SIGNAL_FILE
        if stop_file.exists():
            print(f"[{self.get_timestamp()}] Stop signal file detected. Shutting down...")
            stop_file.unlink()  # Remove the stop signal file
            return True
        return False

    def clear_scraper_completion(self):
        """Clear the scraper completion file to allow re-running all spiders."""
        completed_file = self.project_root / SCRAPER_COMPLETED_FILE

        try:
            # Create the file if it doesn't exist, or clear it if it does
            print(f"[{self.get_timestamp()}] Clearing scraper completion file...")
            with open(completed_file, 'w') as f:
                f.write('')  # Clear the contents but keep the file
            print(f"[{self.get_timestamp()}] Scraper completion file cleared successfully")
        except Exception as e:
            print(f"[{self.get_timestamp()}] Error clearing completion file: {e}")
            print(f"[{self.get_timestamp()}] Continuing anyway...")

    def run_scraper(self):
        """Run the web scraper to collect PDF URLs."""
        try:
            print(f"[{self.get_timestamp()}] Starting web scraper...")

            # Clear the completion file so all spiders run again
            self.clear_scraper_completion()

            # Change to scraper directory
            scraper_dir = self.project_root / 'sf_state_pdf_scan'

            print(f"[{self.get_timestamp()}] Running scrapy spiders...")
            print("-" * 60)

            # Run the scraper with real-time output
            result = subprocess.run(
                [sys.executable, 'run_all_spiders.py'],
                cwd=scraper_dir,
                timeout=7200  # 2 hour timeout
            )

            print("-" * 60)

            if result.returncode == 0:
                print(f"[{self.get_timestamp()}] Web scraper completed successfully")
                return True
            else:
                print(f"[{self.get_timestamp()}] Web scraper failed with return code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print(f"[{self.get_timestamp()}] Web scraper timed out after 2 hours")
            return False
        except Exception as e:
            print(f"[{self.get_timestamp()}] Error running web scraper: {e}")
            return False

    def run_pdf_reports(self):
        """Run the PDF report generation."""
        try:
            print(f"[{self.get_timestamp()}] Starting PDF report generation...")
            create_all_pdf_reports()
            print(f"[{self.get_timestamp()}] PDF report generation completed successfully")
            return True
        except Exception as e:
            print(f"[{self.get_timestamp()}] Error generating PDF reports: {e}")
            return False

    def run_cycle(self):
        """Run a complete cycle of scraping and report generation."""
        print(f"[{self.get_timestamp()}] Starting new cycle...")

        # Run scraper
        scraper_success = self.run_scraper()
        if not scraper_success:
            print(f"[{self.get_timestamp()}] Scraper failed, but continuing with report generation...")

        # Run PDF report generation
        report_success = self.run_pdf_reports()
        if not report_success:
            print(f"[{self.get_timestamp()}] Report generation failed")

        if scraper_success and report_success:
            print(f"[{self.get_timestamp()}] Cycle completed successfully")
        else:
            print(f"[{self.get_timestamp()}] Cycle completed with errors")

        return scraper_success and report_success

    def run(self):
        """Main loop for automated execution."""
        print(f"[{self.get_timestamp()}] Automated PDF Check Runner Started")
        print(f"Loop delay: {LOOP_DELAY} seconds ({LOOP_DELAY/3600:.1f} hours)")
        print("To stop: Press Ctrl+C or create a 'stop.signal' file")
        print("-" * 60)

        cycle_count = 0

        while self.running:
            cycle_count += 1
            print(f"\n[{self.get_timestamp()}] === CYCLE {cycle_count} ===")

            # Check for stop signal
            if self.check_stop_signal():
                break

            # Run the cycle
            try:
                success = self.run_cycle()
            except Exception as e:
                print(f"[{self.get_timestamp()}] Unexpected error in cycle: {e}")
                success = False

            # Check for stop signal again before sleeping
            if self.check_stop_signal() or not self.running:
                break

            # Wait before next cycle
            print(f"[{self.get_timestamp()}] Waiting {LOOP_DELAY} seconds until next cycle...")
            print(f"[{self.get_timestamp()}] Next cycle will start at {datetime.fromtimestamp(time.time() + LOOP_DELAY).strftime('%Y-%m-%d %H:%M:%S')}")

            # Sleep with periodic checks for stop signal
            sleep_interval = 60  # Check every minute
            remaining = LOOP_DELAY

            while remaining > 0 and self.running:
                sleep_time = min(sleep_interval, remaining)
                time.sleep(sleep_time)
                remaining -= sleep_time

                # Check for stop signal during sleep
                if self.check_stop_signal():
                    self.running = False
                    break

        print(f"\n[{self.get_timestamp()}] Automated PDF Check Runner Stopped")
        print(f"Total cycles completed: {cycle_count}")


def main():
    """Main entry point."""
    runner = AutomatedRunner()

    try:
        runner.run()
    except KeyboardInterrupt:
        print(f"\n[{runner.get_timestamp()}] Keyboard interrupt received. Shutting down...")
    except Exception as e:
        print(f"\n[{runner.get_timestamp()}] Fatal error: {e}")
        raise
    finally:
        print(f"[{runner.get_timestamp()}] Cleanup complete. Exiting.")


if __name__ == "__main__":
    main()