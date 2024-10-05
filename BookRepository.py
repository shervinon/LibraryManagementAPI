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
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    return jsonify(books), 200

@app.route('/books/available', methods=['GET'])
def get_available_books():
    cursor.execute("SELECT * FROM books WHERE is_borrowed = FALSE")
    available_books = cursor.fetchall()
    return jsonify(available_books), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
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

@app.route('/users/<int:user_id>/borrowed_books', methods=['GET'])
def get_borrowed_books(user_id):
    cursor.execute("SELECT * FROM books WHERE borrowed_by = %s", (user_id,))
    borrowed_books = cursor.fetchall()
    return jsonify(borrowed_books), 200
# Post Methods (Books)
@app.route('/books', methods=['POST'])
def add_book():
    book_data = request.get_json()
    cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", 
                   (book_data['title'], book_data['author']))
    db.commit()
    book_data['id'] = cursor.lastrowid
    return jsonify(book_data), 201
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
# Post Methods (Books)
@app.route('/books/<int:book_id>/borrow', methods=['POST'])
def borrow_book(book_id):
    borrow_info = request.get_json()
    cursor.execute("SELECT * FROM books WHERE id = %s AND is_borrowed = FALSE", (book_id,))
    book = cursor.fetchone()
    if book:
        cursor.execute("UPDATE books SET is_borrowed = TRUE, borrowed_by = %s WHERE id = %s",
                       (borrow_info['user_id'], book_id))
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
        cursor.execute("UPDATE books SET is_borrowed = FALSE, borrowed_by = NULL WHERE id = %s", (book_id,))
        db.commit()
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        updated_book = cursor.fetchone()
        return jsonify(updated_book), 200
    else:
        return jsonify({'error': 'Book not found or not borrowed by this user'}), 404

@app.route('/books/<int:old_id>/change_id/<int:new_id>', methods=['PUT'])
def change_book_id(old_id, new_id):
    cursor.execute("SELECT * FROM books WHERE id = %s", (old_id,))
    book = cursor.fetchone()
    if book:
        cursor.execute("SELECT * FROM books WHERE id = %s", (new_id,))
        new_id_exists = cursor.fetchone()
        if new_id_exists:
            return jsonify({'error': 'New ID already exists'}), 400
        else:
            cursor.execute("UPDATE books SET id = %s WHERE id = %s", (new_id, old_id))
            db.commit()
            cursor.execute("SELECT * FROM books WHERE id = %s", (new_id,))
            updated_book = cursor.fetchone()
            return jsonify(updated_book), 200
    else:
        return jsonify({'error': 'Book not found'}), 404
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

if __name__ == '__main__':
    app.run(port=2831, debug=True)

