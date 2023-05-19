from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'

DATABASE = 'library.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_user_table():
    with app.app_context():
        conn = get_db()
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL,
                      password TEXT NOT NULL)''')
        conn.commit()

def create_books_table():
    with app.app_context():
        conn = get_db()
        conn.execute('''CREATE TABLE IF NOT EXISTS books
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      author TEXT NOT NULL)''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, password))
        conn.commit()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (username, password))
        #cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()

        if user:
            session['username'] = username
            return redirect('/books')
        else:
           return 'Invalid User Or UnAuthorized User'
        #return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if('username' in session):
       session.pop('username')
    return redirect('/')

@app.route('/books', methods=['GET', 'POST'])
def books():
    username = session.get('username') or ''
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = get_db()
        conn.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        conn.commit()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    return render_template('books.html', books=books, username=username)

@app.route('/books/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = get_db()
        conn.execute("UPDATE books SET title = ?, author = ? WHERE id = ?", (title, author, book_id))
        conn.commit()

        return redirect('/books')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    book = cur.fetchone()

    if book:
        return render_template('edit_book.html', book=book)

    return redirect('/books')

@app.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()

    return redirect('/books')

if __name__ == '__main__':
    create_user_table()
    create_books_table()
    app.run(debug=True)

           
