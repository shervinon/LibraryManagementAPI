from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib

# In-memory database
books = []
users = []

class LibraryHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')[1:]

        if len(path_parts) == 1 and path_parts[0] == 'books':
            self._get_all_books()
        elif len(path_parts) == 2 and path_parts[0] == 'books' and path_parts[1] == 'available':
            self._get_available_books()
        elif len(path_parts) == 2 and path_parts[0] == 'books':
            self._get_book_by_id(int(path_parts[1]))
        elif len(path_parts) == 3 and path_parts[0] == 'books' and path_parts[2] == 'availability':
            self._get_book_availability(int(path_parts[1]))
        elif len(path_parts) == 3 and path_parts[0] == 'users' and path_parts[2] == 'borrowed_books':
            self._get_borrowed_books(int(path_parts[1]))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')[1:]

        if len(path_parts) == 1 and path_parts[0] == 'books':
            self._add_book()
        elif len(path_parts) == 3 and path_parts[0] == 'books' and path_parts[2] == 'borrow':
            self._borrow_book(int(path_parts[1]))
        elif len(path_parts) == 3 and path_parts[0] == 'books' and path_parts[2] == 'return':
            self._return_book(int(path_parts[1]))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def do_PUT(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')[1:]

        if len(path_parts) == 2 and path_parts[0] == 'books':
            self._update_book(int(path_parts[1]))
        elif len(path_parts) == 3 and path_parts[0] == 'books' and path_parts[2] == 'change_id':
            self._change_book_id(int(path_parts[1]))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path_parts = parsed_path.path.split('/')[1:]

        if len(path_parts) == 2 and path_parts[0] == 'books':
            self._delete_book(int(path_parts[1]))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def _get_all_books(self):
        self._set_response()
        self.wfile.write(json.dumps(books).encode('utf-8'))

    def _get_available_books(self):
        available_books = [book for book in books if not book['is_borrowed']]
        self._set_response()
        self.wfile.write(json.dumps(available_books).encode('utf-8'))

    def _get_book_by_id(self, book_id):
        book = next((book for book in books if book['id'] == book_id), None)
        if book:
            self._set_response()
            self.wfile.write(json.dumps(book).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def _get_book_availability(self, book_id):
        book = next((book for book in books if book['id'] == book_id), None)
        if book:
            self._set_response()
            self.wfile.write(json.dumps({'is_borrowed': book['is_borrowed']}).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def _get_borrowed_books(self, user_id):
        borrowed_books = [book for book in books if book.get('borrowed_by') == user_id]
        self._set_response()
        self.wfile.write(json.dumps(borrowed_books).encode('utf-8'))

    def _add_book(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        book = json.loads(post_data)
        book['id'] = len(books) + 1
        book['is_borrowed'] = False
        books.append(book)
        self._set_response(201)
        self.wfile.write(json.dumps(book).encode('utf-8'))

    def _update_book(self, book_id):
        book = next((book for book in books if book['id'] == book_id), None)
        if book:
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            update_data = json.loads(put_data)
            book.update(update_data)
            self._set_response()
            self.wfile.write(json.dumps(book).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def _delete_book(self, book_id):
        global books
        books = [book for book in books if book['id'] != book_id]
        self._set_response(204)
        self.wfile.write(b'')

    def _borrow_book(self, book_id):
        book = next((book for book in books if book['id'] == book_id), None)
        if book and not book['is_borrowed']:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            borrow_info = json.loads(post_data)
            book['is_borrowed'] = True
            book['borrowed_by'] = borrow_info['user_id']
            self._set_response()
            self.wfile.write(json.dumps(book).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Book not found or already borrowed'}).encode('utf-8'))

    def _return_book(self, book_id):
        book = next((book for book in books if book['id'] == book_id), None)
        if book and book['is_borrowed']:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            return_info = json.loads(post_data)
            if book['borrowed_by'] == return_info['user_id']:
                book['is_borrowed'] = False
                del book['borrowed_by']
                self._set_response()
                self.wfile.write(json.dumps(book).encode('utf-8'))
            else:
                self._set_response(403)
                self.wfile.write(json.dumps({'error': 'Book was not borrowed by this user'}).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Book not found or not borrowed'}).encode('utf-8'))

    def _change_book_id(self, old_id, new_id):
        book = next((book for book in books if book['id'] == old_id), None)
        if book:
            if any(book['id'] == new_id for book in books):
                self._set_response(400)
                self.wfile.write(json.dumps({'error': 'New ID already exists'}).encode('utf-8'))
            else:
                book['id'] = new_id
                self._set_response()
                self.wfile.write(json.dumps(book).encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({'error': 'Book not found'}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=LibraryHTTPRequestHandler, port=2831):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
