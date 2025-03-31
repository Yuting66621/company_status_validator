import pandas as pd # type: ignore
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import sys

def DW_business_search(company_name: str):
    service = Service(executable_path = "chromedriver-linux64/chromedriver")
    driver = webdriver.Chrome(service = service)
    
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
        
file_path = sys.argv[1]

try:
    try:
        print("Trying to read the file as CSV with 'latin1' encoding...")
        df = pd.read_csv(file_path, encoding='latin1')
        print("File successfully read as CSV with 'latin1' encoding.")
    except UnicodeDecodeError:
        print("Failed to read as CSV with 'latin1'. Trying with 'utf-8' and errors ignored...")
        df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
        print("File successfully read as CSV with 'utf-8' and errors ignored.")
except pd.errors.ParserError:
    print("The file is not a valid CSV. Attempting to read as an Excel file...")
    try:
        df = pd.read_excel(file_path)
        print("File successfully read as an Excel file.")
    except Exception as e:
        raise ValueError(f"Failed to read the file as either CSV or Excel. Error: {e}")

results = []
for company in df.iloc[:, 0]:
    print(f"Processing: {company}")
    result = DW_business_search(company)
    results.append({"Company Name": company, "Status": result})

results_table = pd.DataFrame(results)
output_file_path = "search_results.xlsx"
results_table.to_excel(output_file_path)
print(f"Search completed. Results saved to '{output_file_path}'.")