import os
import time
import pandas as pd  # Import pandas to read Excel file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Hide the main tkinter window
Tk().withdraw()

# Prompt the user to select the Excel file
print("Please select the Excel file containing the contacts and file paths.")
excel_path = askopenfilename(
    title="Select Excel File",
    filetypes=[("Excel Files", "*.xlsx;*.xls")]
)

if not excel_path:
    print("No file selected. Exiting the program.")
    exit()

# Dynamic path setup
base_dir = os.path.dirname(os.path.abspath(__file__))  # Get current directory
chrome_profile = os.path.join(base_dir, "Profile")  # Profile folder in current directory
chromedriver_path = os.path.join(base_dir, "chromedriver.exe")  # Path to chromedriver in current folder

# Selenium setup
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={chrome_profile}")  # Use dynamic profile folder
service = Service(chromedriver_path)  # Use dynamic chromedriver path
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://web.whatsapp.com/")

wait = WebDriverWait(driver, 10)

# Wait until WhatsApp Web is fully loaded
wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and @data-tab='3']")))

# Read the Excel file
data = pd.read_excel(excel_path)

# Function to search for a target
def search_target(target_name):
    try:
        search_box_xpath = "//div[@contenteditable='true' and @data-tab='3']"
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))

        search_box.click()
        search_box.clear()
        search_box.send_keys(target_name)
        time.sleep(2)  # Allow search results to load

        x_arg = f'//span[@title="{target_name}"]'
        try:
            target_element = WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.XPATH, x_arg)))
            target_element.click()
        except Exception:
            print(f"Contact '{target_name}' not found after waiting for 10 seconds.")
            search_box.click()
            search_box.clear()
            search_box.send_keys("\ue009" + "\ue003" * 50)  # Simulate Ctrl+A and multiple backspaces
            return False

        search_box.click()
        search_box.clear()
        search_box.send_keys("\ue009" + "\ue003" * 50)  # Simulate Ctrl+A and multiple backspaces

        return True
    except Exception as e:
        print(f"Error: Contact '{target_name}' not found: {str(e)}")
        try:
            search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
            search_box.click()
            search_box.clear()
            search_box.send_keys("\ue009" + "\ue003" * 50)  # Simulate Ctrl+A and multiple backspaces
        except Exception as clear_exception:
            print(f"Failed to clear search box: {str(clear_exception)}")
        return False

# Function to send a document
def send_document(file_path, target):
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found. Skipping...")
            return

        # Locate the attachment button and click it
        attachment_button_xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span'
        attachment_button = wait.until(EC.presence_of_element_located((By.XPATH, attachment_button_xpath)))
        attachment_button.click()

        # Locate the hidden input element for the document upload
        file_input_xpath = '//input[@accept="*"]'  # File input accepts all file types
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, file_input_xpath)))
        file_input.send_keys(file_path)  # Send the file path

        # Wait for the Send button to appear
        time.sleep(2)  # Ensure file has time to upload fully
        send_button_xpath = '//span[@data-icon="send"] | //div[@role="button" and @aria-label="Send"]'

        # Retry mechanism for Send button
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, send_button_xpath)))
        send_button.click()
        print(f"Document '{file_path}' sent successfully to {target}!")
    except Exception as e:
        print(f"Failed to send document '{file_path}' to {target}: {str(e)}")

# Loop through each row in the Excel file
for index, row in data.iterrows():
    target = row['Recipient']  # Target name
    document_path = row['File_Path']  # File path or directory

    if not os.path.isabs(document_path):
        document_path = os.path.join(base_dir, document_path)  # Handle relative paths

    # Locate the target chat
    print(f"Searching for '{target}'...")
    time.sleep(2)  # Add delay before searching for the next target
    if not search_target(target):
        print(f"Skipping '{target}' as it could not be located.")
        continue

    # Check if the path is a directory
    if os.path.isdir(document_path):
        print(f"'{document_path}' is a directory. Sending all files inside...")
        for file_name in os.listdir(document_path):
            file_path = os.path.join(document_path, file_name)
            if os.path.isfile(file_path):
                send_document(file_path, target)
    else:
        send_document(document_path, target)

# Close browser
time.sleep(10)
driver.quit()
