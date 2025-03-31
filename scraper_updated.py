'Selenium Test'

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
import time
import pandas as pd
import logging

# reading the list
file_path = 'AI project - Confidential UNC Startups 10162024.xls (1).csv'
companies = pd.read_csv(file_path, encoding = 'Latin1')

# dropping duplicates
companies_unique = companies.drop_duplicates(subset='Company')
company_names = companies_unique['Company']
print(company_names)
# Initialize WebDriver
service = Service(executable_path="chromedriver.exe") # Copy path to chromedriver here
driver = webdriver.Chrome()

def search_nc_businesses(company_names):
    driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed
    results = []
    
    for company in company_names:
        try:
            # Navigate to NC Secretary of State business search page
            driver.get("https://www.sosnc.gov/online_services/search/by_title/_Business_Registration")
            
            
            select_element = driver.find_element(By.ID, 'Words')
            # Create a Select object
            select = Select(select_element)
            try:
                select.select_by_value("EXACT")
                print("Selected by exact name")
            except NoSuchElementException: # type: ignore
                print("Option not found.")

            # Locate search bar on the website
            input_element = driver.find_element(By.ID, 'SearchCriteria')
            input_element.send_keys(company, Keys.ENTER)
            
            # Wait for results and get count
            time.sleep(2)  # Brief delay to allow results to load
            
            try:
                print(f"Starting search for: {company}")
                
                # Wait for search results page to load
                time.sleep(2)  # Keep the pause for stability
                
                # Find the wrapper div and get the first span with the record count
                wrapper = driver.find_element(By.CLASS_NAME, "usa-section")
                records_span = wrapper.find_element(By.TAG_NAME, "span")
                span_text = records_span.text
                
                number = span_text.split(":")[-1].strip()
                record_count = number if number else "0"

                if int(record_count) > 0:
                    try:
                        # Wait until the results section is present
                        results_section = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "resultsSection")))
                        print("Results section found.")
        
                        # Locate all accordion headings (buttons) within the results section
                        accordion_buttons = results_section.find_elements(By.CSS_SELECTOR, ".usa-accordion__heading .usa-accordion__button")
                        print(f"Found {len(accordion_buttons)} accordion buttons.")

                        for index, button in enumerate(accordion_buttons, start=1):
                            try:
                                # Scroll the button into view
                                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.5)  # Brief pause to ensure scrolling is complete
                
                                # Click the button if it's not already expanded
                                is_expanded = button.get_attribute("aria-expanded")
                                if is_expanded.lower() != "true":
                                    button.click()
                                    print(f"Clicked accordion button {index}.")
                                    time.sleep(0.5)  # Wait for the content to expand
                                else:
                                    print(f"Accordion button {index} is already expanded.")
                
                                # Locate the corresponding content div using aria-controls attribute
                                aria_controls = button.get_attribute("aria-controls")
                                content_div = results_section.find_element(By.ID, aria_controls)
                
                                # Wait until the content div is visible
                                WebDriverWait(driver, 1).until(
                                    EC.visibility_of(content_div)
                                )
                
                                # Extract required information from the content div
                                legal_name = extract_field(content_div, "Legal")
                                sosid = extract_field(content_div, "Sosid:")
                                date_formed = extract_field(content_div, "Date formed:")
                                status = extract_field(content_div, "Status:")
                
                                # Append the extracted data to the list
                                results.append({
                                    "Legal Name": legal_name,
                                    "Records Found": record_count,
                                    "SOSID": sosid,
                                    "Date Formed": date_formed,
                                    "Status": status

                                })
                                for record in results:
                                    for key, value in record.items():
                                        # Replace non-breaking spaces with regular spaces
                                        value = value.replace('\xa0', ' ')
                                        # Remove unnecessary prefixes (e.g., 'name: ' from 'Legal Name')
                                        if key == 'Legal Name' and 'name: ' in value:
                                            value = value.replace('name: ', '')
                                        # Strip leading and trailing whitespace
                                        record[key] = value.strip()
                                        
                                print(f"Extracted data for item {index}: {results[-1]}")
                            
                            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                                print(f"Error processing accordion button {index}: {e}")
                                continue  # Proceed to the next button
                            except Exception as e:
                                print(f"Unexpected error for accordion button {index}: {e}")
                                continue

                    except TimeoutException:
                        print("Timeout: Results section not found.")
                        return []
                    except Exception as e:
                        logging.error(f"An unexpected error occurred while extracting information: {e}")
                        return []
            except Exception as e:
                print(f"Specific error: {str(e)}")
                results.append({
                    'company': company,
                    'result': 'No results found'
                })
        except Exception as e:
            results.append({
                'company': company,
                'result': f'Error: {str(e)}'
            }) 
    driver.quit()
    return results        

def extract_field(content_div, field_label):
    try:
        # Locate the div containing the field label
        field_div = content_div.find_element(By.XPATH, f".//div[span[@class='boldSpan' and contains(text(), '{field_label}')]]")
        # Extract the text after the label
        field_text = field_div.get_attribute("innerText").split(field_label)[-1].strip()
        return field_text
    except NoSuchElementException:
        print(f"Field '{field_label}' not found.")
        return ""

search_results = search_nc_businesses(company_names)
# result to a list
ncsos_result = pd.DataFrame(search_results, columns=['Legal Name', 'Records Found', 'SOSID', 'Date Formed', 'Status'])
ncsos_result.to_csv('ncsos_results.csv', index=False)
while True:
    pass
