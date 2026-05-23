# Data Validator Scrapers

![version](https://img.shields.io/badge/version-1.0.0-blue)
![python](https://img.shields.io/badge/python-3.6+-green)
![selenium](https://img.shields.io/badge/selenium-latest-orange)

A tool for validating company information by checking their active/inactive status through global business registries.

**Main Script**:
- **OpenCorporates Company Status Checker** (`opencorporates_checker.py`): Validates company active/inactive status by searching OpenCorporates

**Reference Scripts** (from previous work):
- `dw_scraper.py`: Delaware business registry scraper (reference implementation)
- `nc_scraper.py`: North Carolina Secretary of State scraper (reference implementation)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
  - [OpenCorporates Checker](#opencorporates-checker)
- [Reference Scrapers](#reference-scrapers)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.6+**: Required to run the scripts
- **Google Chrome**: The latest version is recommended 
- **Basic command-line knowledge**: For running the scripts.   
 ***NOTE: Accessing the command-line***: If you are on a windows computer, you can find your *command-line interface* (CLI) by pressing the ⊞ key or entering your start menu and typing "powershell".   
 If you are on a MacOS computer, you can find a similar CLI by clicking on the magnifying glass in the top right corner of your screen and typing "terminal".

## Installation

1. Clone or download this repository to your local machine.

2. Install the required Python packages:

```bash
pip install selenium pandas openpyxl
```

These packages are used for:
- `selenium`: Web automation to interact with browser
- `pandas`: Data handling and CSV/Excel operations
- `openpyxl`: Excel file support for pandas

## Setup

### ChromeDriver Installation

Both scrapers require ChromeDriver to control Chrome:

1. Update Chrome to the latest version

2. Download ChromeDriver from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/#stable)
   - Select the "stable" version
   - Choose the download that matches your operating system
   - For visual guidance, see this [tutorial video](https://www.youtube.com/watch?v=NB8OceGZGjA)

3. Setup based on your operating system:

   **Windows**:
   - Extract the downloaded ZIP file
   - Place `chromedriver.exe` in the same folder as the scraper scripts

   **macOS/Linux**:
   - Extract the ChromeDriver executable to a folder (e.g., `chromedriver-linux64`)
   - Make it executable: `chmod +x chromedriver-linux64/chromedriver`

### Input File Preparation

Prepare a spreadsheet (CSV or Excel) with company names:
1. Create a file with company names in the first column
2. For the NC scraper, ensure the file has a column named 'Employment Company Name'
3. Save it in an accessible location (the same folder as the scripts is recommended)

## Usage

### OpenCorporates Checker

This is the main script for validating company status through OpenCorporates, a comprehensive international business registry database.

1. Run the script with your input file (CSV or Excel):
   ```bash
   python opencorporates_checker.py your_company_list.csv
   ```

2. Results:
   - Reads company names from the first column of your input file
   - Outputs a file with company status: `active`, `inactive`, or `No result found`
   - Includes exact and related match columns for manual verification
   - Handles OpenCorporates CAPTCHA with optional manual verification in GUI mode
   - Supports both CSV and Excel output formats

## Reference Scrapers

The following scripts were used as reference implementations:

### Delaware Scraper

The Delaware scraper checks if companies are registered in Delaware's business registry.

1. Run the script with your input file as a command-line argument:
   ```bash
   python dw_scraper.py your_company_list.csv
   ```

2. Results are saved in `search_results.xlsx`

### North Carolina Scraper

The North Carolina scraper retrieves company information from NC Secretary of State.

1. Run the script with your input file as a command-line argument:
   ```bash
   python nc_scraper.py your_company_list.csv
   ```

2. Results are saved in `ncsos_results.csv`

## Troubleshooting

### Common Issues

1. **ChromeDriver version mismatch**:
   - Error: `SessionNotCreatedException: Message: session not created`
   - Solution: Make sure the ChromeDriver version matches your Chrome browser version

2. **File encoding issues**:
   - Both scripts attempt to handle different encodings (especially Latin1)
   - If problems persist, try saving your input file as Latin-1 encoded

3. **Path errors**:
   - Make sure the path to ChromeDriver is correct for your operating system
   - For Windows, use `chromedriver.exe`
   - For Linux, use the path to the extracted ChromeDriver (e.g., `chromedriver-linux64/chromedriver`)

4. **Column name errors in NC scraper**:
   - Ensure your input file has a column named exactly 'Employment Company Name'
   - Check for any spacing or capitalization differences

5. **Infinite loop in NC scraper**:
   - The NC scraper ends with a `while True: pass` statement that will keep the script running
   - Press Ctrl+C to stop the script after it completes the search
   - Consider removing this line if you want the script to terminate automatically
