import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to fetch CSR amount for a company
def fetch_csr_amount(company_name):
    try:
        # Set up Selenium WebDriver options
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (no browser window)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Initialize WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Search query
        search_query = f"CSR amount of {company_name}"
        url = f"https://www.google.com/search?q={search_query}"
        driver.get(url)

        # Wait for the page to load (minimal time)
        driver.implicitly_wait(3)

        # Extract the entire page content
        page_content = driver.find_element(By.TAG_NAME, "body").text

        # Use regex to find the CSR amount
        csr_pattern = r"Rs\.?\s?\d+\.?\d*\s?Cr\.?"  # Matches "Rs. 215.7 Cr" or similar patterns
        match = re.search(csr_pattern, page_content)

        csr_amount = "Not Found"
        if match:
            csr_amount = match.group()
            print(f"CSR Amount for {company_name}: {csr_amount}")
        else:
            print(f"CSR Amount for {company_name} not found.")
        driver.quit()
        return csr_amount
    except Exception as e:
        print(f"An error occurred while fetching CSR for {company_name}: {e}")
        return "Not Found"

# Function to extract contact information (address, email, phone) of a company
def extract_contact_info(company_name):
    try:
        # Search query for the company contact us page
        search_query = f"{company_name} contact us"
        search_url = f"https://www.google.com/search?q={search_query}"

        # Set user-agent to mimic a real browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Make a request to search for the company contact page
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            print(f"Error: Unable to fetch search results for {company_name}. Status code {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first link to the contact page in the search results
        contact_url = None
        for link in soup.find_all('a', href=True):
            if "contact" in link['href'].lower():
                contact_url = link['href']
                break

        if not contact_url:
            print(f"Contact page link not found for {company_name}.")
            return None

        # Now fetch the contact page
        if not contact_url.startswith('http'):
            contact_url = 'https://www.google.com' + contact_url

        contact_response = requests.get(contact_url, headers=headers)

        if contact_response.status_code != 200:
            print(f"Error: Unable to fetch contact page for {company_name}. Status code {contact_response.status_code}")
            return None

        contact_soup = BeautifulSoup(contact_response.text, 'html.parser')

        # Extract contact info (address, email, phone)
        address = None
        address_tags = contact_soup.find_all(['address', 'p', 'div'], text=True)
        address_keywords = ["address", "location", "headquarters", "office", "company"]
        
        for tag in address_tags:
            text = tag.get_text().strip()
            if any(keyword in text.lower() for keyword in address_keywords):
                address = text
                break

        # If no address found in tags, try to look for a general address-like pattern
        if not address:
            address_pattern = re.compile(r'\d{1,5}\s[\w\s]+(?:St|Ave|Rd|Blvd|Drive|Lane|Circle|Pkwy|Way)[,\.]?\s[\w\s]+(?:[A-Z]{2})?\s\d{5}')
            address_match = address_pattern.search(contact_response.text)
            if address_match:
                address = address_match.group(0)

        # Extracting the email
        email = None
        email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        email_match = email_pattern.search(contact_response.text)
        if email_match:
            email = email_match.group(0)

        # Extracting the phone number
        phone = None
        phone_pattern = re.compile(r"\+?\d{1,4}?[-.\s]??\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}")
        phone_match = phone_pattern.search(contact_response.text)
        if phone_match:
            phone = phone_match.group(0)


        # Returning the extracted information
        return {
            "address": address if address else "Not found",
            "email": email if email else "Not found",
            "phone": phone if phone else "Not found"
        }

    except Exception as e:
        print(f"An error occurred while extracting contact info for {company_name}: {e}")
        return None

# Function to process each company in parallel
def process_company(company_name):
    # Fetch CSR amount
    csr_amt = fetch_csr_amount(company_name)
    # Fetch contact info
    contact_info = extract_contact_info(company_name)

    # If contact info is found, return the data
    if contact_info:
        return {
            "Company Name": company_name,
            "Location": contact_info["address"],
            "Email": contact_info["email"],
            "Phone": contact_info["phone"],
            "CSR Amount": csr_amt
        }
    else:
        return {
            "Company Name": company_name,
            "Location": "Not found",
            "Email": "Not found",
            "Phone": "Not found",
            "CSR Amount": csr_amt
        }

# List of companies to process
companies = companies = [
    "Reliance Industries Limited", "Tata Consultancy Services", "HDFC Bank", "Infosys", 
    "Hindustan Unilever", "ICICI Bank", "State Bank of India", "Bharti Airtel", 
    "Kotak Mahindra Bank", "Wipro", "HCL Technologies", "Asian Paints", "ITC Limited", 
    "Maruti Suzuki India", "Larsen & Toubro", "Axis Bank", "Bajaj Finance", "Nestlé India", 
    "Mahindra & Mahindra", "Sun Pharmaceutical Industries", "Tata Steel", "UltraTech Cement", 
    "Titan Company", "Power Grid Corporation of India", "NTPC Limited", 
    "Oil and Natural Gas Corporation", "Bajaj Finserv", "IndusInd Bank", "JSW Steel", 
    "Hindalco Industries", "Tech Mahindra", "Grasim Industries", 
    "Adani Ports and Special Economic Zone", "Tata Motors", "Divi's Laboratories", 
    "Bharat Petroleum Corporation", "Indian Oil Corporation", "Coal India", 
    "Britannia Industries", "Shree Cement", "Eicher Motors", "Dr. Reddy's Laboratories", 
    "Hero MotoCorp", "Cipla", "Pidilite Industries", "Bajaj Auto", "Marico", 
    "DLF Limited", "HDFC Life Insurance", "SBI Life Insurance", 
    "Zee Entertainment Enterprises", "Godrej Consumer Products", "Tata Power", 
    "GAIL (India)", "Ambuja Cements", "Adani Green Energy", "Adani Transmission", 
    "Apollo Hospitals Enterprise", "ICICI Prudential Life Insurance", "United Spirits", 
    "Motherson Sumi Systems", "Lupin Limited", "Bank of Baroda", "Punjab National Bank", 
    "Biocon", "Hindustan Zinc", "Torrent Pharmaceuticals", "Siemens India", 
    "Bosch India", "Ashok Leyland", "Havells India", "Exide Industries", "Voltas", 
    "Bharat Electronics", "Mahanagar Gas", "Petronet LNG", "Gujarat Gas", "Tata Chemicals", 
    "Adani Enterprises", "Page Industries", "Colgate-Palmolive India", "Dabur India", 
    "Berger Paints", "Castrol India", "GlaxoSmithKline Pharmaceuticals", "Jubilant FoodWorks", 
    "LIC Housing Finance", "Piramal Enterprises", "Shriram Transport Finance", 
    "Indiabulls Housing Finance", "Manappuram Finance", "Muthoot Finance", 
    "IDFC First Bank", "Yes Bank", "Federal Bank", "City Union Bank", "RBL Bank", 
    "Canara Bank", "Union Bank of India", "IDBI Bank"
]
# List to store company data
company_data = []

# Using ThreadPoolExecutor to process companies in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(process_company, companies)

# Collect results
company_data.extend(results)

# Create a pandas DataFrame
df = pd.DataFrame(company_data)

# Save to CSV
df.to_csv("company_csr_report.csv", index=False)

print("CSR report saved to 'company_csr_report.csv'.")
