from flask import Flask, request, jsonify

app = Flask(__name__)

books = []
users = []

@app.route('/books', methods = ['GET'])
def get_all_books():
    return jsonify(books), 200

@app.route('/books/available', methods = ['GET'])
def get_available_books():
    available_books = [book for book in books if not book.get('is borrowed', False)]
    return jsonify(available_books), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        return jsonify(book), 200
    else:
        return jsonify({'error': 'not found'}), 404
    
@app.route('/books/<int:book_id>/availability', methods=['GET'])
def get_book_availability(book_id):
    book = next((book for book in books if book['id'] == book_id),None)
    if book:
        return jsonify({'is borrowed' : book.get('is_borrowed', False)}), 200
    else:
        return jsonify({'error' : 'not found'}), 404
    
@app.route('/users/<int:user_id>/borrowed_books', methods=['GET'])
def get_borrowed_books(user_id):
    borrowed_books = [book for book in books if book.get('borrowed_by') == user_id]
    return jsonify(borrowed_books), 200

@app.route('/books', methods=['POST'])
def add_book():
    book = request.get_json()
    book['id'] = len(books)+1
    book['is_borrowed'] = False
    books.append(book)
    return jsonify(book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book:
        update_data = request.get_json()
        book.update(update_data)
        return jsonify(book), 200
    else:
        return jsonify({'error' : 'not found'}), 404
    
@app.route('/books/<int:book_id>', methods = ['DELETE'])
def delete_book(book_id):
    global books
    books = [book for book in books if book['id'] != book_id]
    return '', 204

@app.route('/books/<int:book_id>/borrow', methods = ['POST'])
def borrow_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book and not book.get('is_borrowed', False):
        borrow_info = request.get_json()
        book['is_borrowed'] = True
        book['borrowed_by'] = borrow_info['user_id']
        return jsonify(book), 200
    else:
        return jsonify({'error' : 'book not found or has been borrowed by other users'}), 404
    
@app.route('/books/<int:book_id>/return', methods=['POST'])
def return_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book and book.get('is_borrowed', False):
        return_info = request.get_json()
        if book['borrowed_by'] == return_info['user_id']:
            book['is_borrowed'] = False
            del book['borrowed_by']
            return jsonify(book), 200
        else:
            return jsonify({'error' : 'book was not borrowed by this user'}), 403
    else:
        return jsonify({'error': 'Book not found or not borrowed'}), 404
    
@app.route('/books/<int:old_id>/change_id/<int:new_id>', methods=['PUT'])
def change_book_id(old_id,new_id):
    book = next((book for book in books if book['id'] == old_id), None)
    if book:
        if any(book['id'] == new_id for book in books):
            return jsonify({'error' : 'new ID already exists'}), 400
        else:
            book['id'] = new_id
            return jsonify(book), 200
    else:
        return jsonify({'error' : 'book not found'}), 404
    
if __name__ == '__main__':
    app.run(port=2831, debug=True)
