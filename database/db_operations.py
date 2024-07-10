import mysql.connector
from mysql.connector import Error, pooling
from .db_config import DB_CONFIG
import json
from datetime import datetime

# Create a connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **DB_CONFIG
)

def get_connection():
    """Get a connection from the pool"""
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            return connection
    except Error as err:
        print(f"Error: '{err}'")
    return None

def create_table():
    """Creates tables if they do not exist."""
    connection = get_connection()
    if connection is None:
        print("Failed to get connection from pool.")
        return

    cursor = connection.cursor()
    create_calculation_results_table_query = """
    CREATE TABLE IF NOT EXISTS calculation_results (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        calculation_data JSON, 
        price_without_rail FLOAT, 
        price_with_rail FLOAT, 
        timestamp DATETIME,
        reference_height FLOAT,
        output_image MEDIUMBLOB,
        company_name VARCHAR(255),
        customer_name VARCHAR(255),
        customer_street VARCHAR(255),
        customer_city VARCHAR(255),
        customer_zipcode VARCHAR(10),
        customer_phone VARCHAR(20),
        customer_email VARCHAR(255)
    ) ENGINE=INNODB;
    """
    
    create_error_form_submissions_table_query = """
    CREATE TABLE IF NOT EXISTS error_form_submissions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(255),
        customer_name VARCHAR(255) NOT NULL,
        customer_email VARCHAR(255) NOT NULL,
        customer_phone VARCHAR(255) NOT NULL,
        customer_street VARCHAR(255) NOT NULL,
        customer_zipcode VARCHAR(255) NOT NULL,
        customer_city VARCHAR(255) NOT NULL,
        error_message TEXT NOT NULL,
        submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=INNODB;
    """
    
    try:
        cursor.execute(create_calculation_results_table_query)
        cursor.execute(create_error_form_submissions_table_query)
        connection.commit()
        print("Tables created successfully")
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()
        connection.close()

def insert_calculation_result(calculation_data, total_width, total_height, customer_data=None):
    connection = get_connection()
    if connection is None:
        print("Failed to get connection from pool.")
        return

    cursor = connection.cursor()

    # Ensure calculation_data is a dictionary with the expected keys
    expected_keys = ["calculation_data", "price_without_rail", "price_with_rail", "reference_height", "output_image"]
    if not all(key in calculation_data for key in expected_keys):
        raise ValueError(f"calculation_data must be a dictionary with keys: {', '.join(expected_keys)}")

    timestamp = datetime.now()

    company_name = customer_data.get("company_name", "") if customer_data else ""
    customer_name = customer_data.get("customer_name", "") if customer_data else ""
    customer_street = customer_data.get("customer_street", "") if customer_data else ""
    customer_city = customer_data.get("customer_city", "") if customer_data else ""
    customer_zipcode = customer_data.get("customer_zipcode", "") if customer_data else ""
    customer_phone = customer_data.get("customer_phone", "") if customer_data else ""
    customer_email = customer_data.get("customer_email", "") if customer_data else ""

    insert_query = """
    INSERT INTO calculation_results (
        calculation_data, 
        price_without_rail, 
        price_with_rail, 
        timestamp, 
        reference_height, 
        total_width, 
        total_height, 
        output_image, 
        company_name, 
        customer_name, 
        customer_street, 
        customer_city, 
        customer_zipcode, 
        customer_phone, 
        customer_email
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (
        json.dumps(calculation_data["calculation_data"]),
        calculation_data["price_without_rail"],
        calculation_data["price_with_rail"],
        timestamp,
        calculation_data["reference_height"],
        total_width, 
        total_height, 
        calculation_data["output_image"],
        company_name,
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
    finally:
        cursor.close()
        connection.close()

def insert_error_form_submission(data):
    connection = get_connection()
    if connection is None:
        print("Failed to get connection from pool.")
        return

    try:
        cursor = connection.cursor()
        query = """INSERT INTO error_form_submissions 
                   (company_name, customer_name, customer_email, customer_phone, customer_street, customer_zipcode, customer_city, error_message) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (
            data['company_name'], 
            data['customer_name'], 
            data['customer_email'], 
            data['customer_phone'], 
            data['customer_street'], 
            data['customer_zipcode'], 
            data['customer_city'], 
            data['error_message']
        ))
        connection.commit()
        cursor.close()
    except Error as e:
        print("Failed to insert record into error_form_submissions table", e)
    finally:
        connection.close()

def close_connection(connection):
    """Closes the database connection."""
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
