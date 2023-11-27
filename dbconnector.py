import duckdb
from flask import Flask, jsonify
from faker import Faker
import random

app = Flask(__name__)

def init_db():
    conn = duckdb.connect('./resources/books.db', read_only=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS books (id STRING, title STRING, author STRING, year INTEGER, details STRING)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS orders (id STRING, book_id STRING, customer_name STRING, address STRING, phone_number STRING, payment_method STRING, total_price FLOAT)")
    conn.close()


def mock_data():
    fake = Faker()

    book_data = []
    for _ in range(20):
        book_id = fake.uuid4()
        title = fake.catch_phrase()
        author = fake.name()
        year = fake.year()
        details = fake.text(100)
        book_data.append((book_id, title, author, year, details))

    conn_books = duckdb.connect('./resources/books.db', read_only=False)
    conn_books.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?)", book_data)
    conn_books.close()

    order_data = []
    conn_books = duckdb.connect('./resources/books.db', read_only=False)
    books_ids = conn_books.execute("SELECT id FROM books").fetchall()
    conn_books.close()

    for _ in range(20):
        order_id = fake.uuid4()
        book_id = random.choice(books_ids)[0]
        customer_name = fake.name()
        address = fake.address()
        phone_number = fake.phone_number()
        payment_method = fake.random_element(elements=('Credit Card', 'Cash'))
        total_price = round(random.uniform(10.0, 100.0), 2)

        order_data.append((order_id, book_id, customer_name, address, phone_number, payment_method, total_price))

    conn_orders = duckdb.connect('./resources/books.db', read_only=False)
    conn_orders.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", order_data)
    conn_orders.close()


# from google.cloud import storage
# import os


# def download_blob(bucket_name, source_blob_name, destination_file_name):
#     """Downloads a blob from the bucket."""
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(source_blob_name)
#     blob.download_to_filename(destination_file_name)
#
#
# def get_db_conn():
#     bucket_name = os.environ.get('BUCKET_NAME')
#     db_file = 'books.db'  # Name of your database file in the bucket
#     temp_db_path = '/tmp/books.db'
#
#     download_blob(bucket_name, db_file, temp_db_path)
#
#     # Now, connect to the database using the temporary path
#     conn = duckdb.connect(temp_db_path, read_only=False)
#     return conn


def get_db_conn():
    return duckdb.connect('./resources/books.db', read_only=False)

def close_conn(conn):
    conn.close()
