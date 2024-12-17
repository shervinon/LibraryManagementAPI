## Files

1. **BookRepository.py**:  
   This is the main Python script that sets up a basic HTTP server for managing books and users. The following API routes are available:

   ### Book Management
   - `GET /books`: Retrieve all books.
   - `GET /books/available`: Get all available (not borrowed) books.
   - `GET /books/{id}`: Get details of a specific book by its ID.
   - `GET /books/{id}/availability`: Check if a specific book is available or borrowed.
   - `POST /books`: Add a new book.
   - `POST /books/{id}/borrow`: Borrow a book (requires user ID in request body).
   - `POST /books/{id}/return`: Return a borrowed book (requires u  ser ID in request body).
   - `PUT /books/{id}`: Update an existing book's information.
   - `PUT /books/{old_id}/change_id/{new_id}`: changing an specific book's ID.
   - `DELETE /books/{id}`: Delete a book by its ID.

   ### User Management
   - `GET /users`: Retrieve all users.
   - `GET /users/{id}`: Get details of a specific user by its ID.
   - `GET /users/{id}/borrowed_books`: Retrieve a list of books borrowed by a specific user.
   - `POST /users`: Add a user.
   - `PUT /users/{id}`: Update an existing user's information.
   - `DELETE /users/{id}`: Delete a user by its ID.

3. **database_setup.sql**:  
   This SQL script sets up the MySQL database and tables required for the library management system. The script creates two tables:
   
   - `books`: Stores information about each book, including its ID, title, author, and borrowing status.
   - `users`: Stores user details, such as user ID and name.

## How to Use

### Step 1: Setting up the MySQL Database
Run the **database_setup.sql** script in your MySQL database to create the required tables.

### Step 2: Running the Python HTTP Server
Run the BookRepository.py script to start the HTTP server.
The server will start on port 2831. You can use Postman or any HTTP client to interact with the API.
