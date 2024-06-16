# Library Management API

This project is a Library Management API that caters to librarians and users. The API provides functionalities for managing the library's book collection and allows users to borrow and check the availability of books.

## Features

### For Librarians:
- **Add a New Book**: `POST /books`
  - Add a new book to the library's collection. Requires sending data like title, author, ISBN, and genre in the request body (JSON format).
  
- **Retrieve Book Information**: `GET /books/:id`
  - Retrieve information about a specific book using its unique ID.
  
- **Update Book Details**: `PUT /books/:id`
  - Update details of an existing book (e.g., mark it borrowed, update genre). Data for update should be sent in the request body.
  
- **Remove a Book**: `DELETE /books/:id`
  - Remove a book from the library's collection.

### For Users (Borrowers):
- **Get List of All Books**: `GET /books`
  - Get a list of all books in the library.

- **Get List of Available Books**: `GET /books/available`
  - Get a list of all available books (not borrowed).

- **Check Book Availability**: `GET /books/:id/availability`
  - Check the availability of a specific book (available or borrowed).
  
- **Borrow a Book**: `POST /books/:id/borrow`
  - Borrow a book (if available). This involves user authentication and updating the book's status.
  
- **Get Borrowed Books**: `GET /users/:id/borrowed_books`
  - Retrieve a list of books currently borrowed by a specific user identified by their ID.

### Additional Features
- **Return a Book**: `POST /books/:id/return`
  - Return a borrowed book.

- **Change Book ID**: `PUT /books/:id/change_id`
  - Change the ID of a book.

## Technical Details

- **Data Persistence**: Uses in-memory storage for simplicity. Can be extended to use SQLite or a relational database.
- **Error Handling**: Proper error handling for various scenarios like invalid data formats, resource not found, unauthorized access, and database errors. Returns appropriate HTTP status codes and informative error messages.
- **Input Validation**: Validates user input to ensure titles and author names are strings, ISBNs are in a valid format, etc.

## Usage

### Adding a New Book
- **Endpoint**: `POST /books`
- **Request Body**:
    ```json
    {
        "title": "Book Title",
        "author": "Author Name",
        "ISBN": "123-4567891234",
        "genre": "Fiction"
    }
    ```

### Retrieving a Book Information
- **Endpoint**: `GET /books/:id`

### Updating Book Details
- **Endpoint**: `PUT /books/:id`
- **Request Body**:
    ```json
    {
        "title": "Updated Book Title",
        "author": "Updated Author Name",
        "ISBN": "123-4567891234",
        "genre": "Non-Fiction"
    }
    ```

### Removing a Book
- **Endpoint**: `DELETE /books/:id`

### Getting List of All Books
- **Endpoint**: `GET /books`

### Getting List of Available Books
- **Endpoint**: `GET /books/available`

### Checking Book Availability
- **Endpoint**: `GET /books/:id/availability`

### Borrowing a Book
- **Endpoint**: `POST /books/:id/borrow`
- **Request Body**:
    ```json
    {
        "user_id": 1
    }
    ```

### Returning a Book
- **Endpoint**: `POST /books/:id/return`
- **Request Body**:
    ```json
    {
        "user_id": 1
    }
    ```

### Getting Borrowed Books by a User
- **Endpoint**: `GET /users/:id/borrowed_books`

### Changing Book ID
- **Endpoint**: `PUT /books/:id/change_id`
- **Request Body**:
    ```json
    {
        "new_id": 10
    }
    ```
