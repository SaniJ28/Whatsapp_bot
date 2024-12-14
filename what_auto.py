from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Set Chrome options
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:/Users/sanid/Desktop/whatsapp-automation/Profile")  # New profile directory

# Use Service to specify ChromeDriver path
service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com/")
wait = WebDriverWait(driver, 300)

# Target contact and message
target = '"Riddhi"'  # Replace with the name of your contact
message = "Hello"
number_of_times = 10  # Number of times to send the message

# Locate the target contact
contact_path = f'//span[contains(@title,{target})]'
contact = wait.until(EC.presence_of_element_located((By.XPATH, contact_path)))
contact.click()

# Send the message multiple times
for x in range(number_of_times):
    # Fetch the message input box inside the loop
    message_box_path = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p'
    message_box = wait.until(EC.presence_of_element_located((By.XPATH, message_box_path)))
    
    # Send the message
    message_box.send_keys(message + Keys.ENTER)
    print(f"Message {x+1} sent")
    time.sleep(1.5)  # Shorter delay
