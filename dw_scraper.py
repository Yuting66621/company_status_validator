import pandas as pd  # type: ignore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import sys
from typing import List, Dict, Any, Union


def search_delaware_business(company_name: str) -> str:
    """
    Search for a company in the Delaware business registry.
    
    Args:
        company_name: The name of the company to search for
        
    Returns:
        A string indicating whether records were found
    """
    service = Service(executable_path="chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get("https://icis.corp.delaware.gov/Ecorp/EntitySearch/NameSearch.aspx")
        
        search_field = driver.find_element(by=By.ID, value="ctl00_ContentPlaceHolder1_frmEntityName")
        search_field.send_keys(company_name)
        
        driver.find_element(by=By.ID, value="ctl00_ContentPlaceHolder1_btnSubmit").click()
        time.sleep(5)
        
        try:
            no_records_element = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_divCountsMsg")
            if no_records_element.is_displayed():
                return f"No records found for {company_name}."
        except:
            pass
                
        return f"Records available for {company_name}."
    
    finally:
        driver.quit()


def read_input_file(file_path: str) -> pd.DataFrame:
    """
    Read company names from a CSV or Excel file.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        DataFrame containing the company data
        
    Raises:
        ValueError: If the file cannot be read as CSV or Excel
    """
    # Try reading as CSV with different encodings
    try:
        print("Trying to read the file as CSV with 'latin1' encoding...")
        df = pd.read_csv(file_path, encoding='latin1')
        print("File successfully read as CSV with 'latin1' encoding.")
        return df
    except UnicodeDecodeError:
        print("Failed to read as CSV with 'latin1'. Trying with 'utf-8' and errors ignored...")
        try:
            df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
            print("File successfully read as CSV with 'utf-8' and errors ignored.")
            return df
        except pd.errors.ParserError:
            pass  # Continue to try Excel format
    except pd.errors.ParserError:
        pass  # Continue to try Excel format
        
    # Try reading as Excel
    print("Attempting to read as an Excel file...")
    try:
        df = pd.read_excel(file_path)
        print("File successfully read as an Excel file.")
        return df
    except Exception as e:
        raise ValueError(f"Failed to read the file as either CSV or Excel. Error: {e}")


def process_companies(companies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process each company in the dataframe and search for it.
    
    Args:
        companies_df: DataFrame containing company names in the first column
        
    Returns:
        DataFrame with search results
    """
    results = []
    
    for company in companies_df.iloc[:, 0]:
        print(f"Processing: {company}")
        result = search_delaware_business(company)
        results.append({"Company Name": company, "Status": result})
    
    return pd.DataFrame(results)


def main(input_file_path: str, output_file_path: str = "search_results.xlsx") -> None:
    """
    Main function to orchestrate the business search process.
    
    Args:
        input_file_path: Path to the input file with company names
        output_file_path: Path where results will be saved (default: search_results.xlsx)
    """
    # Read input file
    df = read_input_file(input_file_path)
    
    # Process companies
    results_df = process_companies(df)
    
    # Save results
    results_df.to_excel(output_file_path)
    print(f"Search completed. Results saved to '{output_file_path}'.")


if __name__ == "__main__":
    # Use command line arguments or default output path
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        main(sys.argv[1])