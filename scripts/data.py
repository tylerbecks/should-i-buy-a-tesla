import sqlite3
import logging


class DataPersistence:
    """
    A class to handle data persistence using SQLite.
    """

    def __init__(self, db_name='tesla_inventory.db'):
        """
        Initializes the database connection and sets up the database.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = self._setup_database()
        self.cursor = self.conn.cursor()

    def _setup_database(self):
        """
        Sets up the SQLite database connection and creates the table if it doesn't exist.

        Returns:
            sqlite3.Connection: A connection object to the SQLite database.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Create a table to store vehicle data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                VIN TEXT UNIQUE NOT NULL,
                Year INTEGER NOT NULL,
                Model TEXT NOT NULL,
                Trim TEXT NOT NULL,
                Price INTEGER NOT NULL,
                PriceAfterTaxCredit INTEGER,
                Mileage INTEGER NOT NULL,
                CleanHistory BOOLEAN NOT NULL,
                FSD BOOLEAN NOT NULL,
                ExteriorColor TEXT NOT NULL,
                Wheels TEXT NOT NULL,
                Interior TEXT NOT NULL
            )
        ''')
        conn.commit()
        return conn

    def insert_vehicle_data(self, data_list):
        """
        Inserts a list of vehicle data dictionaries into the database.

        Args:
            data_list (list): A list of dictionaries containing vehicle data.
        """
        for data in data_list:
            try:
                vehicle_tuple = (
                    data.get('VIN'),
                    data.get('Year'),
                    data.get('Model'),
                    data.get('Trim'),
                    data.get('Price'),
                    data.get('PriceAfterTaxCredit'),
                    data.get('Mileage'),
                    data.get('CleanHistory'),
                    data.get('FSD'),
                    data.get('ExteriorColor'),
                    data.get('Wheels'),
                    data.get('Interior'),
                )

                # Insert data into the database
                self.cursor.execute('''
                    INSERT OR IGNORE INTO inventory (
                        VIN, Year, Model, Trim, Price, PriceAfterTaxCredit, Mileage, CleanHistory, FSD, ExteriorColor, Wheels, Interior
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', vehicle_tuple)
                self.conn.commit()
            except Exception as e:
                logging.error(f"Error inserting data into the database: {e}")

    def fetch_all_data(self):
        """
        Fetches all the vehicle data from the database.

        Returns:
            list: A list of dictionaries containing vehicle data.
        """
        self.cursor.execute('SELECT * FROM inventory')
        columns = [column[0] for column in self.cursor.description]
        data_list = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        return data_list

    def close(self):
        """
        Closes the database connection.
        """
        self.cursor.close()
        self.conn.close()
