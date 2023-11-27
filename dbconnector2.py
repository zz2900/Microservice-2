import os
from google.cloud import storage
import duckdb

bname = 'united-park-406303.appspot.com'
# Google Cloud Storage functions
def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

def get_db_conn():
    """Gets a connection to the database, downloading it if necessary."""
    bucket_name = os.environ.get('BUCKET_NAME')
    print("Bucket Name:", bucket_name)
    db_file = 'books.db'
    temp_db_path = '/tmp/books.db'

    # Download the database file from Cloud Storage to a temp location
    download_blob(bucket_name, db_file, temp_db_path)

    # Connect to the database using the temporary path
    conn = duckdb.connect(temp_db_path, read_only=False)
    return conn, temp_db_path

def close_conn(conn, temp_db_path):
    """Closes the database connection and uploads the file back to the bucket."""
    bucket_name = os.environ.get('BUCKET_NAME')

    conn.close()

    # Upload the updated database file back to Cloud Storage
    upload_blob(bucket_name, temp_db_path, 'books.db')

def init_db():
    """Initializes the database with necessary tables."""
    conn, temp_db_path = get_db_conn()
    conn.execute("CREATE TABLE IF NOT EXISTS books (id STRING, title STRING, author STRING, year INTEGER, details STRING)")
    conn.execute("CREATE TABLE IF NOT EXISTS orders (id STRING, book_id STRING, customer_name STRING, address STRING, phone_number STRING, payment_method STRING, total_price FLOAT)")
    close_conn(conn, temp_db_path)

def mock_data():
    """Generates mock data for testing."""
    # This function should be filled with your mock data generation logic
    pass

# Additional functions used in app.py can also be added here.
