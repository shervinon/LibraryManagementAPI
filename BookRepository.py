from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "localsql4030",
    database = "library")

cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    return "Welcome to the Library API", 200

# Book Management
# Get Methods (Books)
@app.route('/books', methods=['GET'])
def get_all_books():
    cursor.execute("""
        SELECT books.*, GROUP_CONCAT(categories.name) AS categories
        FROM books
        LEFT JOIN book_categories ON books.id = book_categories.book_id
        LEFT JOIN categories ON book_categories.category_id = categories.id
        GROUP BY books.id
    """)
    books = cursor.fetchall()
    return jsonify(books), 200

@app.route('/books/available', methods=['GET'])
def get_available_books():
    cursor.execute("""
        SELECT books.*, GROUP_CONCAT(categories.name) AS categories
        FROM books
        LEFT JOIN book_categories ON books.id = book_categories.book_id
        LEFT JOIN categories ON book_categories.category_id = categories.id
        WHERE books.is_borrowed = FALSE
        GROUP BY books.id
    """)
    available_books = cursor.fetchall()
    return jsonify(available_books), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    cursor.execute("""
        SELECT books.*, GROUP_CONCAT(categories.name) AS categories
        FROM books
        LEFT JOIN book_categories ON books.id = book_categories.book_id
        LEFT JOIN categories ON book_categories.category_id = categories.id
        WHERE books.id = %s
        GROUP BY books.id
    """, (book_id,))
    book = cursor.fetchone()
    if book:
        return jsonify(book), 200
    else:
        return jsonify({'error': 'Not Found'}), 404

@app.route('/books/<int:book_id>/availability', methods=['GET'])
def get_book_availability(book_id):
    cursor.execute("SELECT is_borrowed FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if book:
        return jsonify({'is_borrowed': book['is_borrowed']}), 200
    else:
        return jsonify({'error': 'Not Found'}), 404

@app.route('/books/search', methods=['GET'])
def search_books():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query parameter is missing or empty'}), 400

    cursor.execute("""
        SELECT books.*, GROUP_CONCAT(categories.name) AS categories
        FROM books
        LEFT JOIN book_categories ON books.id = book_categories.book_id
        LEFT JOIN categories ON book_categories.category_id = categories.id
        WHERE books.title LIKE %s OR books.author LIKE %s
        GROUP BY books.id
    """, (f"%{query}%", f"%{query}%"))
    books = cursor.fetchall()

    if books:
        return jsonify(books), 200
    else:
        return jsonify({'message': 'No books found matching the query'}), 404

# Post Methods (Books)
@app.route('/books', methods=['POST'])
def add_book():
    book_data = request.get_json()
    cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", 
                   (book_data['title'], book_data['author']))
    db.commit()
    book_data['id'] = cursor.lastrowid
    return jsonify(book_data), 201
@app.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    borrow_info = request.get_json()

    start_date = borrow_info.get('start_date')
    end_date = borrow_info.get('end_date')

    cursor.execute("SELECT * FROM books WHERE id = %s AND is_borrowed = FALSE", (book_id,))
    book = cursor.fetchone()

    if book:
        cursor.execute(
            """
            UPDATE books 
            SET is_borrowed = TRUE, borrowed_by = %s, borrowed_start_date = %s, borrowed_end_date = %s 
            WHERE id = %s
            """,
            (borrow_info['user_id'], start_date, end_date, book_id)
        )
        db.commit()

        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        updated_book = cursor.fetchone()
        return jsonify(updated_book), 200
    else:
        return jsonify({'error': 'Book not found or already borrowed'}), 404

@app.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    return_info = request.get_json()
    
    cursor.execute("SELECT * FROM books WHERE id = %s AND is_borrowed = TRUE", (book_id,))
    book = cursor.fetchone()
    
    if book and book['borrowed_by'] == return_info['user_id']:
        cursor.execute("""
            UPDATE books 
            SET is_borrowed = FALSE, 
                borrowed_by = NULL, 
                borrowed_start_date = NULL, 
                borrowed_end_date = NULL 
            WHERE id = %s
        """, (book_id,))
        db.commit()
        
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        updated_book = cursor.fetchone()
        return jsonify(updated_book), 200
    else:
        return jsonify({'error': 'Book not found or not borrowed by this user'}), 404


# Put Methods (Books)
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    update_data = request.get_json()
    cursor.execute("UPDATE books SET title = %s, author = %s WHERE id = %s",
                   (update_data.get('title'), update_data.get('author'), book_id))
    db.commit()
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    updated_book = cursor.fetchone()
    if updated_book:
        return jsonify(updated_book), 200
    else:
        return jsonify({'error': 'Not Found'}), 404

# Delete Methods (Books)
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    db.commit()
    return '', 204

# User Management
# Get Methods (Users)
@app.route('/users', methods=['Get'])
def get_all_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return jsonify(user), 200
    else:
        return jsonify({'error': 'Not Found'}), 404
    
@app.route('/users/<int:user_id>/borrowed_books', methods=['GET'])
def get_borrowed_books(user_id):
    cursor.execute("SELECT * FROM books WHERE borrowed_by = %s", (user_id,))
    borrowed_books = cursor.fetchall()
    return jsonify(borrowed_books), 200

@app.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '')
    cursor.execute("""
        SELECT * FROM users 
        WHERE name LIKE %s
    """, (f"%{query}%",))
    users = cursor.fetchall()
    return jsonify(users), 200

# Post Methods (Users)
@app.route('/users', methods=['POST'])
def add_user():
    user_data = request.get_json()
    cursor.execute("INSERT INTO users (name) VALUES (%s)", (user_data['name'],))
    db.commit()
    user_data['id'] = cursor.lastrowid
    return jsonify(user_data), 201

# Put Methods (Users)
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    update_data = request.get_json()
    cursor.execute("UPDATE users SET name = %s WHERE id = %s", 
                   (update_data.get('name'), user_id))
    db.commit()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    updated_user = cursor.fetchone()
    if updated_user:
        return jsonify(updated_user), 200
    else:
        return jsonify({'error': 'Not Found'}), 404

# Delete Methods (Users)
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    return '', 204

# Category Management
# Get Methods (Categories)
@app.route('/categories', methods=['GET'])
def get_all_categories():
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    return jsonify(categories), 200

@app.route('/books/<int:book_id>/categories', methods=['GET'])
def get_categories_of_book(book_id):
    cursor.execute("""
        SELECT categories.* 
        FROM categories
        JOIN book_categories ON categories.id = book_categories.category_id
        WHERE book_categories.book_id = %s
    """, (book_id,))
    categories = cursor.fetchall()
    return jsonify(categories), 200

@app.route('/categories/<int:category_id>/books', methods=['GET'])
def get_books_of_category(category_id):
    cursor.execute("""
        SELECT books.* 
        FROM books
        JOIN book_categories ON books.id = book_categories.book_id
        WHERE book_categories.category_id = %s
    """, (category_id,))
    books = cursor.fetchall()
    return jsonify(books), 200

@app.route('/categories/search', methods=['GET'])
def search_categories():
    query = request.args.get('q', '')
    cursor.execute("""
        SELECT * FROM categories 
        WHERE name LIKE %s
    """, (f"%{query}%",))
    categories = cursor.fetchall()
    return jsonify(categories), 200

# Post Methods (Categories)
@app.route('/categories', methods=['POST'])
def add_category():
    category_data = request.get_json()
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_data['name'],))
    db.commit()
    category_data['id'] = cursor.lastrowid
    return jsonify(category_data), 201

@app.route('/books/<string:book_title>/categories/<string:category_name>', methods=['POST'])
def add_book_to_category_by_name(book_title, category_name):
    cursor.execute("SELECT id FROM books WHERE title = %s", (book_title,))
    book = cursor.fetchone()
    
    if not book:
        return jsonify({'error': f"Book '{book_title}' not found"}), 404
    
    book_id = book['id']

    cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
    category = cursor.fetchone()
    
    if not category:
        return jsonify({'error': f"Category '{category_name}' not found"}), 404

    category_id = category['id']

    cursor.execute("INSERT INTO book_categories (book_id, category_id) VALUES (%s, %s)", (book_id, category_id))
    db.commit()
    
    return jsonify({'message': f"Book '{book_title}' added to category '{category_name}'"}), 200
# Delete Methods (Categories)
@app.route('/books/<string:book_title>/categories/<string:category_name>', methods=['DELETE'])
def remove_book_from_category(book_title, category_name):

    cursor.execute("SELECT id FROM books WHERE title = %s", (book_title,))
    book = cursor.fetchone()
    if not book:
        return jsonify({'error': f"Book '{book_title}' not found"}), 404

    cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
    category = cursor.fetchone()
    if not category:
        return jsonify({'error': f"Category '{category_name}' not found"}), 404

    cursor.execute(
        "DELETE FROM book_categories WHERE book_id = %s AND category_id = %s",
        (book['id'], category['id'])
    )
    db.commit()

    return jsonify({'message': f"Book '{book_title}' removed from category '{category_name}'"}), 200



if __name__ == '__main__':
    app.run(port=2831, debug=True)
