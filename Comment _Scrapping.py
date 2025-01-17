#importing all necessary libraris
import time
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import messagebox
from selenium.webdriver.chrome.options import Options  # Import ChromeOptions to enable Incognito mode


# Function to login to LinkedIn
def linkedin_login(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    # Enter username
    driver.find_element(By.ID, "username").send_keys(username)

    # Enter password
    driver.find_element(By.ID, "password").send_keys(password)

    # Click login
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)  # Allow time for login to complete


# Function to scrape comments from a post
def scrape_comments(driver, post_url, post_number):
    driver.get(post_url)
    time.sleep(5)  # Wait for the page to load completely

    print(f"Scraping Post {post_number}...")

    # Scroll and load all comments
    scroll_to_load(driver)

    # Get the users who commented on the post
    commenters = []
    try:
        commenter_elements = driver.find_elements(By.XPATH, "//span[@class='comments-comment-meta__description-title']")
        commenters = [clean_name(commenter.text) for commenter in commenter_elements]
    except Exception as e:
        print(f"Error scraping comments: {e}")

    return commenters


# Scroll the page until all comments are loaded
def scroll_to_load(driver):
    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll to bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new content to load

        # Get new page height after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")

        # If we haven't loaded any new content, stop scrolling
        if new_height == prev_height:
            break
        prev_height = new_height

        # Click "Show More" buttons for comments if available
        try:
            show_more_comments_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Show more')]")
            if show_more_comments_button.is_displayed():
                show_more_comments_button.click()
                time.sleep(3)  # Wait for comments to load
        except:
            pass


# Clean up the name by removing "View" and "Profile" parts
def clean_name(name):
    return name.replace("View", "").replace("profile", "").strip()


# Function to save comments data to an Excel file
def save_comments_to_excel(comments_data, file_name="linkedin_comments_data.xlsx"):
    if not comments_data:
        messagebox.showwarning("No Data", "No comments data found to save.")
        return  # Exit if there is no data

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Comments Data"

    # Write the header row
    ws.append(['Name', 'Points'])

    # Write the comments data
    for user in comments_data:
        ws.append([user, 2])  # All users get 2 points

    # Save the workbook to a file
    wb.save(file_name)
    messagebox.showinfo("Success", f"Comments data saved successfully to {file_name}")


# Function to run scraping and data processing
def run_scraping():
    username = username_entry.get()
    password = password_entry.get()
    post_urls = post_urls_entry.get().split(',')

    # Start Selenium WebDriver with Incognito mode
    options = Options()
    options.add_argument("--incognito")  # Enabling Incognito mode
    service = Service(ChromeDriverManager().install())  # Automatically install ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)  # Pass options to WebDriver

    linkedin_login(driver, username, password)

    all_comments_data = []

    # Start processing each post
    for index, url in enumerate(post_urls, start=1):
        commenters = scrape_comments(driver, url, index)  # Pass post number

        # Append all users (allowing duplicates)
        all_comments_data.extend(commenters)

    # Save comments data to an Excel file
    save_comments_to_excel(all_comments_data, "linkedin_comments_data.xlsx")

    driver.quit()


# GUI for scrapping

### Note Enter Fake ID's Username and passsword ######
root = tk.Tk()
root.title("LinkedIn Comment Scraper")

tk.Label(root, text="LinkedIn Username").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="LinkedIn Password").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Label(root, text="Post URLs (comma separated)").pack()
post_urls_entry = tk.Entry(root)
post_urls_entry.pack()

run_button = tk.Button(root, text="Run Scraping", command=run_scraping)
run_button.pack()  

root.mainloop()
