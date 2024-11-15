import logging
from scraper import TeslaScraper
from data import DataPersistence


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    urls = [
        # Used
        "https://www.tesla.com/inventory/used/ms?arrangeby=plh&zip=90245",
        "https://www.tesla.com/inventory/used/m3?arrangeby=plh&zip=90245",
        "https://www.tesla.com/inventory/used/mx?arrangeby=plh&zip=90245",
        "https://www.tesla.com/inventory/used/my?arrangeby=plh&zip=90245",
        # New
        "https://www.tesla.com/inventory/new/ms?arrangeby=plh&zip=90245",
        "https://www.tesla.com/inventory/new/m3?arrangeby=plh&zip=90245",
        "https://www.tesla.com/inventory/new/mx?arrangeby=plh&zip=90245",
        "https://www.tesla.com/inventory/new/my?arrangeby=plh&zip=90245",
    ]

    for url in urls:
        # Initialize the scraper
        scraper = TeslaScraper(url, headless=False)

        # Initialize the data persistence handler
        db_handler = DataPersistence(db_name='data/tesla_inventory.db')

        try:
            # Scrape the data
            scraper.scroll_to_load_all_listings()
            data_list = scraper.extract_listings()
            logging.info(f"Extracted data from {len(data_list)} listings.")

            # Persist the data
            db_handler.insert_vehicle_data(data_list)
            logging.info("Data has been persisted to the database.")

        finally:
            # Close resources
            scraper.close()
            
    db_handler.close()


if __name__ == '__main__':
    main()
