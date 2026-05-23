import argparse
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote_plus

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


OPENCORPORATES_SEARCH_URL = "https://opencorporates.com/companies?q={query}"


def create_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def read_input_file(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path, encoding="latin1")
    except Exception:
        try:
            return pd.read_csv(file_path, encoding="utf-8")
        except Exception:
            return pd.read_excel(file_path)


def get_company_names(df: pd.DataFrame) -> List[str]:
    first_column = df.iloc[:, 0]
    return [str(value).strip() for value in first_column if str(value).strip()]


def normalize_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"\b(inc|llc|ltd|limited|corp|corporation|co|company|plc)\b", "", name)
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


def is_exact_match(result_name: str, searched_name: str) -> bool:
    return normalize_name(result_name) == normalize_name(searched_name)


def is_related_match(result_name: str, searched_name: str) -> bool:
    result = normalize_name(result_name)
    searched = normalize_name(searched_name)

    if not result or not searched:
        return False

    return searched in result or result in searched


def detect_status(text: str) -> str:
    text = text.lower()

    inactive_words = [
        "inactive",
        "dissolved",
        "liquidated",
        "closed",
        "ceased",
        "dormant",
        "revoked",
        "cancelled",
        "canceled",
        "strike off",
    ]

    if any(word in text for word in inactive_words):
        return "inactive"

    if "active" in text:
        return "active"

    return "unknown"


def has_no_results(driver: webdriver.Chrome) -> bool:
    page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

    no_result_phrases = [
        "no results found",
        "no companies found",
        "did not match any companies",
        "couldn't find any companies",
    ]

    return any(phrase in page_text for phrase in no_result_phrases)


def is_blocked_by_captcha(driver: webdriver.Chrome) -> bool:
    page = driver.page_source.lower()
    return "captcha" in page or "verify you are human" in page or "h-captcha" in page


def extract_results(driver: webdriver.Chrome, searched_name: str) -> List[Dict[str, str]]:
    results = []

    links = driver.find_elements(
        By.XPATH,
        "//a[contains(@href, '/companies/') and normalize-space(text()) != '']",
    )

    seen = set()

    for link in links:
        name = link.text.strip()
        href = link.get_attribute("href") or ""

        if not name or not href:
            continue

        key = (name, href)
        if key in seen:
            continue

        seen.add(key)

        container_text = name

        for xpath in ["./ancestor::li[1]", "./ancestor::div[1]", "./ancestor::div[2]"]:
            try:
                container = link.find_element(By.XPATH, xpath)
                if container.text.strip():
                    container_text = container.text.strip()
                    break
            except Exception:
                pass

        if is_exact_match(name, searched_name):
            match_type = "exact"
        elif is_related_match(name, searched_name):
            match_type = "related"
        else:
            match_type = "other"

        results.append(
            {
                "name": name,
                "url": href,
                "status": detect_status(container_text),
                "match_type": match_type,
            }
        )

    return results


def format_matches(results: List[Dict[str, str]]) -> str:
    if not results:
        return ""

    return "; ".join(
        f"{item['name']} [{item['status']}] - {item['url']}"
        for item in results
    )


def check_company(driver: webdriver.Chrome, company_name: str, timeout: int = 15) -> Dict[str, str]:
    query = quote_plus(company_name)
    url = OPENCORPORATES_SEARCH_URL.format(query=query)

    driver.get(url)

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        pass

    if is_blocked_by_captcha(driver):
        return {
            "Company": company_name,
            "Status": "Blocked by CAPTCHA",
            "Exact Matches": "",
            "Related Matches": "",
        }

    if has_no_results(driver):
        return {
            "Company": company_name,
            "Status": "No result found",
            "Exact Matches": "",
            "Related Matches": "",
        }

    all_results = extract_results(driver, company_name)

    exact_matches = [
        result for result in all_results
        if result["match_type"] == "exact"
    ]

    related_matches = [
        result for result in all_results
        if result["match_type"] in ["related", "other"]
    ]

    if exact_matches:
        statuses = [result["status"] for result in exact_matches]

        if "active" in statuses:
            final_status = "active"
        elif "inactive" in statuses:
            final_status = "inactive"
        else:
            final_status = "unknown"

    elif all_results:
        final_status = "No exact match"

    else:
        final_status = "No result found"

    return {
        "Company": company_name,
        "Status": final_status,
        "Exact Matches": format_matches(exact_matches),
        "Related Matches": format_matches(related_matches),
    }


def process_companies(df: pd.DataFrame, headless: bool = False) -> pd.DataFrame:
    company_names = get_company_names(df)
    driver = create_driver(headless=headless)

    output_rows = []

    try:
        for company_name in company_names:
            print(f"Searching: {company_name}")
            result = check_company(driver, company_name)
            output_rows.append(result)
    finally:
        driver.quit()

    return pd.DataFrame(output_rows)


def normalize_output_base(output_file: str) -> str:
    path = Path(output_file)

    if path.suffix.lower() in [".csv", ".xlsx"]:
        return str(path.with_suffix(""))

    return str(path)


def save_results(df: pd.DataFrame, output_file: str) -> None:
    output_base = normalize_output_base(output_file)

    csv_path = f"{output_base}.csv"
    excel_path = f"{output_base}.xlsx"

    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)

    print(f"Saved results to {csv_path} and {excel_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check company active/inactive status on OpenCorporates."
    )

    parser.add_argument("input_file", help="CSV or Excel file with company names in the first column.")
    parser.add_argument(
        "output_file",
        nargs="?",
        default="opencorporates_results",
        help="Output file base name. CSV and Excel will be created.",
    )
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode.")

    args = parser.parse_args()

    input_df = read_input_file(args.input_file)
    results_df = process_companies(input_df, headless=args.headless)
    save_results(results_df, args.output_file)


if __name__ == "__main__":
    main()