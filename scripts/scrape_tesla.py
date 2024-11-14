from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Load the Tesla website
url = "https://www.tesla.com/inventory/used/m3?arrangeby=plh&zip=90245"
driver.get(url)

# Allow some time for the page to load
time.sleep(5)

try:
    # Locate the h1 element and print its text content
    h1_element = driver.find_element(By.TAG_NAME, "h1")
    print("Page Title (h1):", h1_element.text)
except Exception as e:
    print("Could not find h1 element:", e)

# Close the browser
driver.quit()
