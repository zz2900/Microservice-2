import math
import random
import uuid

from flask import Flask, render_template, request, redirect, jsonify
from flask_graphql import GraphQLView

from dbconnector import get_db_conn, close_conn, init_db, mock_data
from resources.book_resource import TextbookResource
from resources.graphql_schema import schema

app = Flask(__name__)
PER_PAGE = 5
KEYWORD_CACHE = ''
instance = TextbookResource()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/textbook/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = int(request.form['year'])
        details = request.form['details']
        book_id = str(uuid.uuid4())

        conn, temp_db_path = get_db_conn()
        conn.execute(f"INSERT INTO books VALUES ('{book_id}', '{title}', '{author}', {year}, '{details}')")
        close_conn(conn, temp_db_path)

        return redirect('/')

    return render_template('add_book.html')


@app.route('/api/textbook/search', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        # 获取关键词
        keyword = request.form['keyword']
        if keyword:
            conn, temp_db_path = get_db_conn()
            result = conn.execute(f"SELECT COUNT(*) FROM books WHERE title LIKE '%{keyword}%'")
            total_count = result.fetchone()[0]
            close_conn(conn, temp_db_path)
            page = request.args.get('page', 1, type=int)
            total_pages = math.ceil(total_count / PER_PAGE)
            offset = (page - 1) * PER_PAGE
            conn, temp_db_path = get_db_conn()
            result = conn.execute(
                f"SELECT id, title, author, year FROM books WHERE title LIKE '%{keyword}%' LIMIT {PER_PAGE} OFFSET {offset}")
            books = result.fetchall()
            close_conn(conn, temp_db_path)

            return render_template('search_book.html', books=books, total_pages=total_pages, current_page=page,
                                   keyword=keyword)

    elif request.method == 'GET':
        keyword = request.args.get('keyword_cache', '', type=str)
        conn, temp_db_path = get_db_conn()
        result = conn.execute(f"SELECT COUNT(*) FROM books WHERE title LIKE '%{keyword}%'")
        total_count = result.fetchone()[0]
        close_conn(conn, temp_db_path)
        page = request.args.get('page', 1, type=int)
        total_pages = math.ceil(total_count / PER_PAGE)
        offset = (page - 1) * PER_PAGE

        conn , temp_db_path = get_db_conn()
        result = conn.execute(
            f"SELECT id, title, author, year FROM books WHERE title LIKE '%{keyword}%' LIMIT {PER_PAGE} OFFSET {offset}")
        books = result.fetchall()
        close_conn(conn, temp_db_path)

        return render_template('search_book.html', books=books, total_pages=total_pages, current_page=page,
                               keyword=keyword)
    return render_template('search_book.html', books=[], total_pages=0, current_page=0, keyword='')


@app.route('/api/textbook/async_view/<id>')
async def view_textbook_async(id):
    result = await instance.get_book_async(id)
    if result:
        print(result)
        return render_template('view_book.html', book=result['book']['book'], sale=result['sale']['sale'])

    return jsonify({'error': 'Book not found'})


@app.route('/api/textbook/sync_view/<id>')
async def view_textbook_sync(id):
    result = await instance.get_book_sync(id)
    if result:
        print(result)
        return render_template('view_book.html', book=result['book']['book'],  sale=result['sale']['sale'])

    return jsonify({'error': 'Book not found'})


@app.route('/api/textbook/buy/<bookid>', methods=['GET', 'POST'])
def buy_textbook(bookid):
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        payment_method = request.form['payment_method']

        conn, temp_db_path = get_db_conn()
        result = conn.execute(f"SELECT * FROM books WHERE id = '{bookid}'")
        book = result.fetchone()
        close_conn(conn, temp_db_path)

        if book:
            order_id = str(uuid.uuid4())
            print(order_id)

            price = round(random.uniform(10, 100), 2)
            discount = random.randint(0, 50)

            final_price = price * (1 - (discount / 100))

            conn, temp_db_path = get_db_conn()
            conn.execute(
                f"INSERT INTO orders VALUES ('{order_id}', '{book[0]}', '{customer_name}', '{address}', '{phone_number}', '{payment_method}', {final_price})")
            close_conn(conn, temp_db_path)

            return jsonify({"message": "Payment successful"})

        return jsonify({'error': 'Book not found'})

    conn, temp_db_path  = get_db_conn()
    result = conn.execute(f"SELECT * FROM books WHERE id = '{bookid}'")
    book = result.fetchone()
    close_conn(conn, temp_db_path)

    if book:
        return render_template('buy_book.html', book_id=bookid, book_title=book[1], book_author=book[2])

    return jsonify({'error': 'Book not found'})


@app.route('/get_book_info_json/<id>')
def get_book_info(id):
    conn, temp_db_path = get_db_conn()
    result = conn.execute(f"SELECT * FROM books WHERE id = '{id}'")
    book = result.fetchone()
    close_conn(conn, temp_db_path)
    return jsonify({'book': book})


@app.route('/get_book_sale_json/<id>')
def get_book_sale_json(id):
    conn, temp_db_path = get_db_conn()
    result = conn.execute(f"SELECT COUNT(*) FROM orders WHERE book_id = '{id}'")
    sale = result.fetchone()
    close_conn(conn, temp_db_path)
    return jsonify({'sale': sale})

## use graphql to search books
app.add_url_rule('/api/textbook/graphql_search', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
))

# query example
# {
#   books(title: "d") {
#     id
#     title
#     author
#   	year
#     details
#   }
# }

if __name__ == '__main__':
    init_db()
    # mock_data()
    app.run(host='0.0.0.0', port=8000)
