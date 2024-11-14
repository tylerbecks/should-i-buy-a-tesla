import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TeslaScraper:
    """
    A class to scrape Tesla vehicle listings from the Tesla website.
    """

    def __init__(self, url, headless=False):
        """
        Initializes the scraper with the given URL and sets up the WebDriver.

        Args:
            url (str): The URL of the Tesla inventory page to scrape.
            headless (bool): Whether to run the browser in headless mode.
        """
        self.url = url
        self.headless = headless
        self.driver = self._setup_driver()
        self.data_list = []

    def _setup_driver(self):
        """
        Sets up the Chrome WebDriver.

        Returns:
            webdriver.Chrome: An instance of the Chrome WebDriver.
        """
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        # Allow some time for the page to load
        time.sleep(5)
        return driver

    def _find_cards(self):
        """
        Finds all vehicle listing elements on the page.

        Returns:
            list: A list of WebElement objects representing vehicle listings.
        """
        return self.driver.find_elements(By.CSS_SELECTOR, 'main .result')

    def scroll_to_load_all_listings(self):
        """
        Scrolls through the page to load all vehicle listings.
        """
        num_of_listings = len(self._find_cards())
        logging.info(f"Initial number of listings: {num_of_listings}")

        while True:
            # Scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new listings to load
            time.sleep(3)  # Adjust sleep time as needed

            # Wait for the loading indicator to disappear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'tds-loader--show'))
                )
            except Exception as e:
                logging.warning(f"Loading indicator wait exception: {e}")

            # Get the updated list of vehicle listings
            new_vehicle_listings = self._find_cards()
            new_num_of_listings = len(new_vehicle_listings)

            if new_num_of_listings == num_of_listings:
                # No new listings loaded; exit the loop
                logging.info("All listings loaded.")
                break
            else:
                logging.info(f"Loaded {new_num_of_listings - num_of_listings} new listings.")
                num_of_listings = new_num_of_listings

    def _parse_listing(self, listing):
        """
        Parses a vehicle listing element to extract data.

        Args:
            listing (WebElement): A WebElement representing a vehicle listing.

        Returns:
            dict: A dictionary containing extracted data, or None if extraction fails.
        """
        try:
            # Extract data from each listing
            model_info = listing.find_element(By.CSS_SELECTOR, '.result-header h3.tds-text--h4').text.strip()
            trim = listing.find_element(By.CSS_SELECTOR, '.result-header .tds-text_color--10').text.strip()
            year = model_info.split()[0]
            model_name = ' '.join(model_info.split()[1:])

            # Price
            price_element = listing.find_element(By.CLASS_NAME, 'result-purchase-price')
            price_text = price_element.text.strip().replace('$', '').replace(',', '')
            price = int(price_text)

            # Mileage
            mileage_element = listing.find_element(By.CSS_SELECTOR, ".result-basic-info div > span")
            mileage_text = mileage_element.text.strip().replace(' mile odometer', '').replace(',', '')
            mileage = int(mileage_text)

            # VIN
            data_id = listing.get_attribute('data-id')
            # data-id looks like this: "5YJSA1E52MF443774-search-result-container"
            vin = data_id.split('-')[0]

            # Clean History/has accident
            history_icon = listing.find_elements(By.CLASS_NAME, 'inventory-icon--history-clean')
            has_clean_history = len(history_icon) > 0

            # Full Self-Driving (FSD)
            fsd = listing.find_elements(By.CLASS_NAME, 'inventory-icon--autopilot-fsd')
            has_fsd = len(fsd) > 0

            # Exterior color
            exterior_color = listing.find_element(By.CSS_SELECTOR, '.result-regular-features > li:nth-child(1)').text.strip()

            # Wheels
            wheels = listing.find_element(By.CSS_SELECTOR, '.result-regular-features > li:nth-child(2)').text.strip()

            # Interior
            interior = listing.find_element(By.CSS_SELECTOR, '.result-regular-features > li:nth-child(3)').text.strip()

            # Assemble data into a dictionary
            data = {
                'Year': year,
                'Model': model_name,
                'Trim': trim,
                'Price': price,
                'Mileage': mileage,
                'VIN': vin,
                'CleanHistory': has_clean_history,
                'FSD': has_fsd,
                'ExteriorColor': exterior_color,
                'Wheels': wheels,
                'Interior': interior
            }

            return data

        except Exception as e:
            logging.error(f"Error extracting data from a listing: {e}")
            return None

    def extract_listings(self):
        """
        Extracts data from all vehicle listings on the page.

        Returns:
            list: A list of dictionaries containing data from each listing.
        """
        vehicle_listings = self._find_cards()
        logging.info(f"Number of listings found: {len(vehicle_listings)}")

        for listing in vehicle_listings:
            data = self._parse_listing(listing)
            if data:
                self.data_list.append(data)

        return self.data_list

    def close(self):
        """
        Closes the WebDriver and quits the browser.
        """
        self.driver.quit()
