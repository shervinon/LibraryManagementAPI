from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:localsql4030@localhost/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretkey of authorization'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

#models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    is_borrowed = db.Column(db.Boolean, default=False)
    borrowed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    borrower = db.relationship('User', backref='borrowed_books')
    borrowed_start_date = db.Column(db.Date, nullable=True)
    borrowed_end_date = db.Column(db.Date, nullable=True)
    categories = db.relationship('Category', secondary='book_categories', back_populates='books')
    
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    books = db.relationship('Book', secondary='book_categories', back_populates='categories')

class BookCategory(db.Model):
    __tablename__ = 'book_categories'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)

with app.app_context():
    db.create_all()
@app.route('/')
def index():
    return "Welcome to the Library API", 200

# Book Management
# Get Methods (Books)
@app.route('/books', methods=['GET'])
def get_all_books():
    books = Book.query.all()
    result = []
    for book in books:
        result.append({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'is_borrowed': book.is_borrowed,
            'borrowed_by': book.borrower.name if book.borrower else None,
            'categories': [category.name for category in book.categories],
        })
    return jsonify(result), 200

@app.route('/books/available', methods=['GET'])
def get_available_books():
    available_books = Book.query.filter_by(is_borrowed=False).all()
    result = [
        {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'categories': [category.name for category in book.categories]
        }
        for book in available_books
    ]
    return jsonify(result), 200

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'is_borrowed': book.is_borrowed,
            'borrowed_by': book.borrower.name if book.borrower else None,
            'categories': [category.name for category in book.categories]
        }), 200
    else:
        return jsonify({'error': 'Book not found'}), 404

@app.route('/books/<int:book_id>/availability', methods=['GET'])
def get_book_availability(book_id):
    book = Book.query.get(book_id)
    if book:
        return jsonify({'is_borrowed': book.is_borrowed}), 200
    else:
        return jsonify({'error': 'Not Found'}), 404

@app.route('/books/search', methods=['GET'])
def search_books():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query parameter is missing or empty'}), 400

    books = Book.query.filter(
        (Book.title.like(f"%{query}%")) | (Book.author.like(f"%{query}%"))
    ).all()

    if books:
        result = [
            {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'categories': [category.name for category in book.categories]
            }
            for book in books
        ]
        return jsonify(result), 200
    else:
        return jsonify({'message': 'No books found matching the query'}), 404

# Post Methods (Books)
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = Book(title=data['title'], author=data['author'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'id': new_book.id, 'title': new_book.title, 'author': new_book.author}), 201

@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    data = request.get_json()
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    if book.is_borrowed:
        return jsonify({'error': 'Book is already borrowed'}), 400

    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    book.is_borrowed = True
    book.borrowed_by = user.id
    book.borrowed_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    book.borrowed_end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    db.session.commit()
    return jsonify({'message': 'Book borrowed successfully'}), 200

@app.route('/return/<int:book_id>', methods=['POST'])
def return_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    if not book.is_borrowed:
        return jsonify({'error': 'Book is not borrowed'}), 400

    book.is_borrowed = False
    book.borrowed_by = None
    book.borrowed_start_date = None
    book.borrowed_end_date = None
    db.session.commit()
    return jsonify({'message': 'Book returned successfully'}), 200

# Put Methods (Books)
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'}), 200

# Delete Methods (Books)
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200

# User Management
# Get Methods (Users)
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    result = [{'id': user.id, 'name': user.name} for user in users]
    return jsonify(result), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({'id': user.id, 'name': user.name}), 200
    else:
        return jsonify({'error': 'Not Found'}), 404

@app.route('/users/<int:user_id>/borrowed_books', methods=['GET'])
def get_borrowed_books(user_id):
    user = User.query.get(user_id)
    if user:
        borrowed_books = [
            {
                'id': book.id,
                'title': book.title,
                'author': book.author
            }
            for book in user.borrowed_books
        ]
        return jsonify(borrowed_books), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/users/search', methods=['GET'])
def search_users():
    query = request.args.get('query', '')

    if not query.strip():
        return jsonify({'error': 'Query parameter is missing or empty'}), 400

    users = User.query.filter(User.name.like(f"%{query}%")).all()
    result = [{'id': user.id, 'name': user.name} for user in users]

    if not result:
        return jsonify({'message': 'No users found matching the query'}), 404

    return jsonify(result), 200


# Post Methods (Users)
@app.route('/users', methods=['POST'])
def add_user():
    user_data = request.get_json()
    new_user = User(name=user_data['name'], username=user_data['username'], password=user_data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'name': new_user.name, 'username': new_user.username, 'password': new_user.password}), 201

# Put Methods (Users)
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not Found'}), 404

    update_data = request.get_json()
    user.name = update_data.get('name', user.name)
    db.session.commit()
    return jsonify({'message': 'user updated successfully'}), 200

# Delete Methods (Users)
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Not Found'}), 404

    db.session.delete(user)
    db.session.commit()
    return '', 204

# Category Management
# Get Methods (Categories)
@app.route('/categories', methods=['GET'])
def get_all_categories():
    categories = Category.query.all()
    result = [{'id': category.id, 'name': category.name} for category in categories]
    return jsonify(result), 200

@app.route('/books/<int:book_id>/categories', methods=['GET'])
def get_categories_of_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    categories = [{'id': category.id, 'name': category.name} for category in book.categories]
    return jsonify(categories), 200

@app.route('/categories/<int:category_id>/books', methods=['GET'])
def get_books_of_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    books = [{'id': book.id, 'title': book.title, 'author': book.author} for book in category.books]
    return jsonify(books), 200

@app.route('/categories/search', methods=['GET'])
def search_categories():
    query = request.args.get('query', '')
    categories = Category.query.filter(Category.name.like(f"%{query}%")).all()
    result = [{'id': category.id, 'name': category.name} for category in categories]
    return jsonify(result), 200

# Post Methods (Categories)
@app.route('/categories', methods=['POST'])
def add_category():
    category_data = request.get_json()
    new_category = Category(name=category_data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'id': new_category.id, 'name': new_category.name}), 201

@app.route('/books/<string:book_title>/categories/<string:category_name>', methods=['POST'])
def add_book_to_category_by_name(book_title, category_name):
    book = Book.query.filter_by(title=book_title).first()
    if not book:
        return jsonify({'error': f"Book '{book_title}' not found"}), 404

    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return jsonify({'error': f"Category '{category_name}' not found"}), 404

    book.categories.append(category)
    db.session.commit()

    return jsonify({'message': f"Book '{book_title}' added to category '{category_name}'"}), 200
# Delete Methods (Categories)
@app.route('/books/<string:book_title>/categories/<string:category_name>', methods=['DELETE'])
def remove_book_from_category(book_title, category_name):
    book = Book.query.filter_by(title=book_title).first()
    if not book:
        return jsonify({'error': f"Book '{book_title}' not found"}), 404

    category = Category.query.filter_by(name=category_name).first()
    if not category:
        return jsonify({'error': f"Category '{category_name}' not found"}), 404

    book.categories.remove(category)
    db.session.commit()

    return jsonify({'message': f"Book '{book_title}' removed from category '{category_name}'"}), 200

# User Authorization
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(name=data['name'], username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
@app.route('/protected', methods=['GET'])
@jwt_required()  
def protected():
    return jsonify({'message': 'You are viewing a protected route!'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=9282)
