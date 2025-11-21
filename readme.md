# SF State PDF Accessibility Scanner

## Overview

The SF State PDF Accessibility Scanner is an automated system designed to scan San Francisco State University websites for PDF documents and evaluate their accessibility compliance. The system crawls multiple SFSU domains, identifies PDF files, downloads them, and runs comprehensive accessibility checks using industry-standard tools.

## Purpose

This project helps SFSU ensure that all PDF documents hosted on their websites are accessible to users with disabilities, complying with:
- Section 508 of the Rehabilitation Act
- WCAG (Web Content Accessibility Guidelines)
- PDF/UA (Universal Accessibility) standards

## Key Features

- **Automated Web Crawling**: Uses Scrapy framework to systematically scan SFSU websites
- **PDF Discovery**: Identifies and catalogs all PDF documents across multiple SFSU domains
- **Accessibility Validation**: Checks PDFs for accessibility issues using VeraPDF and custom validation tools
- **Database Storage**: Maintains a SQLite database of all discovered PDFs and their accessibility status
- **Report Generation**: Creates detailed HTML and Excel reports for each scanned site
- **Box.com Integration**: Handles PDFs stored on Box.com cloud storage
- **Continuous Monitoring**: Runs on a scheduled basis to continuously monitor PDF accessibility

## System Architecture

### Components

1. **Web Scrapers (Spiders)**
   - Located in: `sf_state_pdf_scan/sf_state_pdf_scan/spiders/`
   - 300+ individual spider files, each targeting a specific SFSU subdomain
   - Built using Scrapy framework for efficient web crawling

2. **PDF Analysis Engine**
   - `conformance_checker.py`: Core module for PDF accessibility validation
   - `pdf_priority.py`: Determines priority level of accessibility issues
   - Uses VeraPDF for PDF/UA compliance checking

3. **Database Layer**
   - SQLite database: `drupal_pdfs.db`
   - Tables:
     - `drupal_site`: Stores website information
     - `drupal_pdf_files`: Catalogs discovered PDFs
     - `pdf_report`: Contains accessibility analysis results
     - `site_user`: User assignments for remediation
     - `failure`: Tracks download/processing failures

4. **Reporting System**
   - `html_report.py`: Generates HTML accessibility reports
   - `data_export.py`: Creates Excel reports for detailed analysis
   - `admin_email.py`: Sends notifications to administrators

5. **Automation Controller**
   - `run.py`: Main orchestration script for automated execution
   - `run_all_spiders.py`: Manages sequential spider execution

## Prerequisites

### Software Requirements

- Python 3.8 or higher
- VeraPDF (for PDF/UA validation)
- Git (for version control)

### Python Dependencies

Install required packages using pip:

```bash
pip install -r requirements.txt
```

Key dependencies include:
- Scrapy (web crawling framework)
- BeautifulSoup4 (HTML parsing)
- Requests (HTTP library)
- Jinja2 (template engine)
- OpenPyXL (Excel file generation)
- PDFMiner.six (PDF text extraction)
- PikePDF (PDF manipulation)
- PyYAML (configuration parsing)
- python-dotenv (environment management)

### External Tools

1. **VeraPDF Installation**
   - Download from: https://verapdf.org/downloads/
   - Install and ensure `verapdf` command is available in system PATH
   - Required for PDF/UA compliance checking

## Setup Instructions

### 1. Clone the Repository

```bash
git clone [repository-url]
cd sf_state_pdf_website_scan
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your local paths:

```env
# Box.com Base Path (adjust for your machine)
BOX_ATI_BASE_PATH=C:\Users\[YourUsername]\Box\ATI\PDF Accessibility

# Project Base Path (adjust for your machine)
PROJECT_BASE_PATH=C:\Users\[YourUsername]\IdeaProjects\sf_state_pdf_website_scan
```

### 3. Update Configuration

Edit `settings.yaml` to configure:
- Database location
- Box.com folder paths
- Email settings
- Report output settings

### 4. Initialize Database

Run the database initialization:

```bash
python database.py
```

This creates the necessary tables in `drupal_pdfs.db`.

### 5. Set Up Box.com Integration (if applicable)

If your organization uses Box.com:
- Ensure Box Drive is installed and synced
- Update Box paths in `.env` file
- Verify folder permissions

## Usage

### Running the Automated Scanner

#### Full Automated Mode

Run the complete scanning and reporting cycle:

```bash
python run.py
```

This will:
1. Clear the spider completion tracker
2. Run all configured spiders sequentially
3. Download and analyze discovered PDFs
4. Generate accessibility reports
5. Wait for the configured interval (default: 1 hour)
6. Repeat the cycle

To stop the automated scanner:
- Press `Ctrl+C`, or
- Create a file named `stop.signal` in the project directory

#### Manual Spider Execution

To run spiders manually:

```bash
cd sf_state_pdf_scan
python run_all_spiders.py
```

### Generating Reports

#### Generate All Reports

```python
from master_functions import create_all_pdf_reports
create_all_pdf_reports()
```

#### Generate Single Site Report

```python
from master_functions import build_single_xcel_report
build_single_xcel_report("example.sfsu.edu")
```

#### Generate HTML Summary Report

```bash
python html_report.py
```

### Checking Individual PDFs

To check a single PDF for accessibility:

```python
from conformance_checker import create_verapdf_report
report = create_verapdf_report("https://example.sfsu.edu/document.pdf")
```

## Output Files

### Reports Location

- **Excel Reports**: `Box\ATI\PDF Accessibility\SF State Website PDF Scans\[domain-name]\`
- **HTML Reports**: Project root directory
- **Database**: `drupal_pdfs.db`

### Report Contents

Excel reports include:
- PDF URL and location
- Accessibility violations count
- Tagged status
- Language settings
- Form presence
- Priority classification
- Download failures

HTML reports provide:
- Overall statistics
- Site-by-site summaries
- High-priority issue tracking
- Trend analysis

## Spider Management

### Adding New Sites

To add a new SFSU site for scanning:

1. Create a new spider file in `sf_state_pdf_scan/sf_state_pdf_scan/spiders/`
2. Follow the naming convention: `[site_name]_spider.py`
3. Use the template structure from existing spiders
4. Update the `start_urls` and domain patterns

Example spider template:

```python
import scrapy
import re
from scrapy.linkextractors import LinkExtractor

class NewSiteSpider(scrapy.Spider):
    name = 'new_site_spider'
    start_urls = ['https://newsite.sfsu.edu']

    def parse(self, response):
        # Extract and follow links
        # Identify PDF files
        # Store results in database
        pass
```

### Monitoring Spider Status

The system tracks completed spiders in:
`sf_state_pdf_scan/sf_state_pdf_scan/completed_spiders.txt`

This file is cleared at the start of each scanning cycle.

## Database Schema

### Key Tables

1. **drupal_site**
   - Stores website domain information
   - Links to Box.com folders
   - Security group assignments

2. **drupal_pdf_files**
   - Catalogs all discovered PDFs
   - Tracks parent pages
   - Monitors 404 status
   - Archive status tracking

3. **pdf_report**
   - Accessibility violation counts
   - PDF metadata (tagged, language, forms)
   - Text type classification
   - Page count

## Troubleshooting

### Common Issues

1. **VeraPDF Not Found**
   - Ensure VeraPDF is installed and in PATH
   - Test with: `verapdf --version`

2. **Box.com Path Errors**
   - Verify Box Drive is running
   - Check folder sync status
   - Update paths in `.env` file

3. **Spider Timeouts**
   - Adjust timeout in `run.py` (default: 2 hours)
   - Check network connectivity
   - Review spider efficiency

4. **Database Lock Errors**
   - Ensure only one instance is running
   - Check file permissions
   - Close database viewers

### Logging

Logs are generated with timestamps for:
- Spider execution status
- PDF download attempts
- Accessibility check results
- Report generation

## Maintenance

### Regular Tasks

1. **Database Cleanup**
   - Archive old scan results
   - Remove duplicate entries
   - Optimize database performance

2. **Spider Updates**
   - Update URLs for redesigned sites
   - Add new SFSU domains
   - Remove deprecated sites

3. **Report Template Updates**
   - Modify HTML/Excel templates as needed
   - Update accessibility criteria
   - Adjust priority classifications

### Backup Procedures

1. **Database Backup**
   - Located in: `database-backups/`
   - Run regular backups of `drupal_pdfs.db`

2. **Report Archives**
   - Excel reports auto-backup to `backups/` folder
   - Maintain monthly archives

## Security Considerations

- The system handles SSL certificate errors gracefully
- Respects robots.txt when configured
- Implements rate limiting to avoid overwhelming servers
- Stores no sensitive user data
- PDF content is analyzed but not permanently stored

## Performance Optimization

- **Concurrent Requests**: Set to 16 (adjustable in settings.py)
- **Download Delay**: 0.05 seconds between requests
- **AutoThrottle**: Enabled to adapt to server response times
- **Spider Parallelization**: Runs sequentially to maintain consistency

## Support and Contact

For issues, questions, or contributions:
- Report issues at: [GitHub repository issues page]
- Email support: access@sfsu.edu
- Documentation updates: Submit pull requests

## License

This project is developed for San Francisco State University's accessibility compliance efforts.

---

Last Updated: November 2024
Version: 1.0