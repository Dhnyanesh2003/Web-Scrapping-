#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import pandas as pd
from collections import OrderedDict
import time

# Read and load the dataframe
df = pd.read_csv("paste CSV file location")

# For January month only
df = df.iloc[0:40, :]  # Adjust the slice as needed

# Initialize WebDriver service and options (outside the loop)
service = Service()
options = webdriver.ChromeOptions()
options.add_experimental_option('detach', True)
options.add_argument("--incognito")

# LinkedIn login credential cookie (replace with actual credentials)
cookie = {
    "name": "li_at",
    "value": "add your cookie value here"
    # Replace with actual cookie value
}

# List to hold all user data
scraped_data = []

# Function to scrape a single LinkedIn post URL
def scrape_linkedin(post_url):
    user_dict = OrderedDict()  # Initialize user_dict here to ensure it's always defined
    browser = webdriver.Chrome(service=service, options=options)

    try:
        # Set the LinkedIn authentication cookie and navigate to the URL
        browser.get('https://www.linkedin.com')
        browser.add_cookie(cookie)
        browser.get(post_url)

        # Explicit wait for the page to load
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Try clicking the "plus button" to expand the user list
        try:
            click1 = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'social-details-social-counts__count-value') and contains(@aria-label, 'reactions')]"))
            )
            click1.click()
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".inline-flex.full-width")))
        except TimeoutException:
            print(f"Plus button not found. Skipping to scrape visible users for URL: {post_url}")

        # Continuously load and scrape user data
        previous_user_count = 0
        while True:
            try:
                divs = browser.find_elements(By.CSS_SELECTOR, ".inline-flex.full-width")
                new_users_found = False

                for div in divs:
                    try:
                        user_element = div.find_element(By.CSS_SELECTOR, ".link-without-hover-state.ember-view")
                        user_href = user_element.get_attribute('href')
                        user_name = user_element.find_element(By.CSS_SELECTOR, ".text-view-model").text

                        if user_name not in user_dict:
                            user_dict[user_name] = user_href
                            new_users_found = True

                    except NoSuchElementException:
                        continue

                # Attempt to find and click the "Show more results" button
                try:
                    show_more_button = WebDriverWait(browser, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".scaffold-finite-scroll__load-button"))
                    )
                    show_more_button.click()
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".inline-flex.full-width")))
                    print("Clicked 'Show more' and loading more users...")
                except (NoSuchElementException, TimeoutException):
                    if not new_users_found:
                        print("No more new users to load or the button is missing.")
                        break

            except StaleElementReferenceException:
                print("Stale element reference exception occurred, re-locating elements.")
                time.sleep(1)
                continue

        # Handle visible users not in divs
        if not user_dict:
            li_elements = browser.find_elements(By.CSS_SELECTOR, ".social-details-reactors-facepile__list-item")
            for li in li_elements:
                try:
                    user_element = li.find_element(By.CSS_SELECTOR, ".social-details-reactors-facepile__profile-link")
                    user_href = user_element.get_attribute('href')
                    user_name = user_element.text

                    if user_name not in user_dict:
                        user_dict[user_name] = user_href
                except NoSuchElementException:
                    continue

    except Exception as e:
        print(f"An error occurred for URL: {post_url}, Error: {e}")

    finally:
        # Store the scraped data as individual rows
        for user_name, user_href in user_dict.items():
            scraped_data.append({
                'post_url': post_url,
                'user_link': user_href,
                'user_name': user_name
            })
        print(f"Scraped {len(user_dict)} unique users from {post_url}")

        # Close the browser after each URL
        browser.quit()

# Main execution
if __name__ == "__main__":
    try:
        # Iterate through each post URL in the DataFrame
        for index, row in df.iterrows():
            post_url = row['post_url']
            scrape_linkedin(post_url)
    except KeyboardInterrupt:
        print("Script interrupted by user. Saving data...")

        # Save the scraped data to a CSV file before exiting
        if scraped_data:
            output_df = pd.DataFrame(scraped_data)
            output_df.to_csv('scraped_data_interrupted.csv', index=False)
            print("Data saved to 'scraped_data_interrupted.csv'.")

    finally:
        print("Final cleanup done.")
        # Convert the scraped data to a DataFrame and save it as a CSV file
        if scraped_data:
            output_df = pd.DataFrame(scraped_data)
            output_df.to_csv('scraped_likes.csv', index=False)
            print("Scraping completed and data saved to 'scraped_likes.csv'.")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




