import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from functools import wraps
from .db_config import DB_CONFIG
import json
from datetime import datetime

connection = None  # Global variable to store the connection

def create_db_connection():
    """Establishes a database connection using the credentials defined in db_config.py."""
    global connection
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        print("MySQL-Datenbankverbindung erfolgreich")
        return connection
    except Error as err:
        print(f"Fehler: '{err}'")
        return None

def reconnect_db():
    """Re-establishes the database connection."""
    global connection
    if connection is not None and connection.is_connected():
        close_connection(connection)
    connection = create_db_connection()
    print("Datenbankverbindung wurde erneuert")

def close_connection(connection):
    """Closes the database connection."""
    if connection.is_connected():
        connection.close()
        print("MySQL-Verbindung ist geschlossen")

def reconnect_cursor(func):
    """Decorator to reconnect the cursor and retry the function if a disconnect occurs."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global connection
        try:
            return func(*args, **kwargs)
        except mysql.connector.Error as err:
            if err.errno in [errorcode.CR_SERVER_LOST, errorcode.CR_SERVER_GONE_ERROR, errorcode.CR_CONNECTION_ERROR]:
                print("Verbindung verloren, versuche erneut zu verbinden...")
                reconnect_db()
                return func(*args, **kwargs)
            else:
                print(f"Fehler: '{err}'")
                raise
    return wrapper

@reconnect_cursor
def create_table(connection):
    """Creates tables if they do not exist."""
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
        print("Tabellen erfolgreich erstellt")
    except Error as err:
        print(f"Fehler: '{err}'")

@reconnect_cursor
def insert_calculation_result(connection, calculation_data, total_width, total_height, customer_data=None):
    cursor = connection.cursor()

    # Ensure calculation_data is a dictionary with the expected keys
    expected_keys = ["calculation_data", "price_without_rail", "price_with_rail", "reference_height", "output_image"]
    if not all(key in calculation_data for key in expected_keys):
        raise ValueError(f"calculation_data muss ein Wörterbuch mit Schlüsseln sein: {', '.join(expected_keys)}")

    timestamp = datetime.now()

    customer_name = customer_street = customer_city = customer_zipcode = customer_phone = customer_email = ""
    company_name = ""

    if customer_data is not None:
        company_name = customer_data.get("company_name", "")
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
        print("Abfrage erfolgreich")
    except Error as err:
        print(f"Fehler: '{err}'")

@reconnect_cursor
def insert_error_form_submission(connection, data):
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
        print("Fehler beim Einfügen des Datensatzes in die Tabelle error_form_submissions", e)

# Call create_db_connection on script start
create_db_connection()

# Example usage with automatic reconnection
try:
    create_table(connection)
except Error as e:
    print(f"Fehler bei der Erstellung der Tabellen: {e}")
    reconnect_db()
    create_table(connection)
