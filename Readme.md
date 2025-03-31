# Data Validator Scrapers

![version](https://img.shields.io/badge/version-1.0.0-blue)
![python](https://img.shields.io/badge/python-3.6+-green)
![selenium](https://img.shields.io/badge/selenium-latest-orange)

A tool for validating business entity information by scraping state business registration websites. This project includes two scrapers:
- **Delaware Business Entity Search**: Checks if companies exist in Delaware's business registry
- **North Carolina Business Entity Search**: Searches for company information in North Carolina's Secretary of State database

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
  - [Delaware Scraper](#delaware-scraper)
  - [North Carolina Scraper](#north-carolina-scraper)
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

### Delaware Scraper

The Delaware scraper checks if companies are registered in Delaware's business registry.

1. If needed, update the ChromeDriver path in the `search_delaware_business` function:
   ```python
   service = Service(executable_path="chromedriver-linux64/chromedriver")  # Update if your path is different
   ```

2. Run the script with your input file as a command-line argument:
   ```bash
   python dw_scraper.py your_company_list.csv
   ```

   You can also specify an output file name as a second argument:
   ```bash
   python dw_scraper.py your_company_list.csv custom_output_name.xlsx
   ```

3. Results:
   - The script will process each company in your list
   - Progress information appears in the terminal
   - Results are saved in `search_results.xlsx` (or your custom output name)
   - The Excel file shows which companies have records available in Delaware

### North Carolina Scraper

The North Carolina scraper retrieves company information from NC Secretary of State.

1. Before running, update the ChromeDriver path in the script:
   ```python
   service = Service(executable_path="chromedriver.exe")  # Update with your path
   ```

2. Run the script with your input file as a command-line argument:
   ```bash
   python nc_scraper.py your_company_list.csv
   ```

3. Results:
   - The script will search for each company from the 'Employment Company Name' column
   - Results are saved in `ncsos_results.csv`
   - The CSV file contains company names, record counts, SOSID, formation dates, and status

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
