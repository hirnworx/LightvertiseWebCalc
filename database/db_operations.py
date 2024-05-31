# db_operations.py

import mysql.connector
from mysql.connector import Error
from .db_config import DB_CONFIG
import json
from datetime import datetime

def create_db_connection():
    """Establishes a database connection using the credentials defined in db_config.py."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        print("MySQL Database connection successful")
        return connection
    except Error as err:
        print(f"Error: '{err}'")
        return None

def create_table(connection):
    """Creates a table if it does not exist, for storing calculation results."""
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS calculation_results (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        calculation_data JSON, 
        price_without_rail FLOAT, 
        price_with_rail FLOAT, 
        timestamp DATETIME,
        reference_height FLOAT,
        output_image MEDIUMBLOB,
        customer_name VARCHAR(255),
        customer_street VARCHAR(255),
        customer_city VARCHAR(255),
        customer_zipcode VARCHAR(10),
        customer_phone VARCHAR(20),
        customer_email VARCHAR(255)
    )  ENGINE=INNODB;
    """
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def insert_calculation_result(connection, calculation_data, customer_data=None):
    cursor = connection.cursor()

    # Ensure calculation_data is a dictionary with the expected keys
    expected_keys = ["calculation_data", "price_without_rail", "price_with_rail", "reference_height", "output_image"]
    if not all(key in calculation_data for key in expected_keys):
        raise ValueError(f"calculation_data must be a dictionary with keys: {', '.join(expected_keys)}")

    timestamp = datetime.now()

    customer_name = customer_street = customer_city = customer_zipcode = customer_phone = customer_email = ""

    if customer_data is not None:
        customer_name = customer_data.get("customer_name", "")
        customer_street = customer_data.get("customer_street", "")
        customer_city = customer_data.get("customer_city", "")
        customer_zipcode = customer_data.get("customer_zipcode", "")
        customer_phone = customer_data.get("customer_phone", "")
        customer_email = customer_data.get("customer_email", "")

    insert_query = """
    INSERT INTO calculation_results (
        calculation_data, 
        price_without_rail, 
        price_with_rail, 
        timestamp, 
        reference_height, 
        output_image, 
        customer_name, 
        customer_street, 
        customer_city, 
        customer_zipcode, 
        customer_phone, 
        customer_email
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (
        json.dumps(calculation_data["calculation_data"]),
        calculation_data["price_without_rail"],
        calculation_data["price_with_rail"],
        timestamp,
        calculation_data["reference_height"],
        calculation_data["output_image"],
        customer_name,
        customer_street,
        customer_city,
        customer_zipcode,
        customer_phone,
        customer_email
    )

    try:
        cursor.execute(insert_query, values)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def close_connection(connection):
    """Closes the database connection."""
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
