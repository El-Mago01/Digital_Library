from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
import logging

logging.basicConfig (
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

app_name="MAGO_Library"
app = Flask(__name__)
"""
Setting the Database URI
Configure the database connection by specifying the database Uniform Resource Identifier (URI) after the initialized 
Flask app in app.py, which is a string that specifies the connection details and location of a database. 
It is commonly used to establish a connection between an application and a database management system (DBMS). 
The URI contains information such as the DBMS type, host, port, database name, and authentication credentials.

For this demonstration we will be using an SQLite3 database. To avoid path issues with Flask, 
we will set the database URI using an absolute path:
"""
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app) #This will connect the Flask app to the flask-sqlalchemy code.
#This code only needs to run once.
with app.app_context():
    db.create_all()

"""
Helper functions
-----------------------------------------------------------------------
"""

def get_authors_name_and_ids()->list:
    name_ids=[]
    stmt = db.select(Author).order_by(Author.name.asc())
    authors = db.session.execute(stmt).scalars().all()
    for author in authors:
        name_ids.append((author.name, author.author_id))
    return name_ids

def get_all_books_and_authors(direction:str="asc")->list:
    books=[]
    stmt = db.select(Book, Author).join(Author, Book.author_id == Author.author_id,).order_by(Book.title.asc())
    result = db.session.execute(stmt).all()
    for book, author in result:
        print(f"{book.title} - {author.name}")
        books.append((book.title, author.name, book.publication_year))
    return books

"""
Routes
-----------------------------------------------------------------------
"""
@app.route('/', methods=['GET'])
def home():

    all_books = get_all_books_and_authors()
    print(type(all_books))
    for book in all_books:
        print(type(book))
    return render_template('home.html', app_name=app_name, all_books=all_books)




@app.route('/add_author', methods=['POST','GET'])
def add_author():
    if request.method == 'GET':
        logging.info("Adding Author with GET request")
        return render_template('add_author.html')
    logging.info("Adding Author with POST request")
    author_name = request.form.get('author_name',"")
    author_birth_date = request.form.get('birth_year',"")
    author_death_date = request.form.get('death_year',"")
    received_author = Author(
        name=author_name,
        birth_date=author_birth_date,
        death_date=author_death_date
    )
    logging.info(f"This author will be stored: {received_author}")
    db.session.add(received_author)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/add_book', methods=['POST','GET'])
def add_book():
    if request.method == 'GET':
        authors=get_authors_name_and_ids()

        logging.info(f"Adding a book with GET request and the following authors: {authors}")
        return render_template('add_book.html', authors=authors)
    logging.info("Adding a book with POST request")
    isbn = request.form.get('book_isbn')
    title = request.form.get('book_title')
    author_id = request.form.get('author_id')
    publication_year = request.form.get('publication_year')
    received_book = Book(
        title=title,
        author_id=author_id,
        isbn=isbn,
        publication_year=publication_year
    )
    logging.info(f"This book will be stored: {received_book}")
    db.session.add(received_book)
    db.session.commit()
    return redirect(url_for("home"))


app.run(host='0.0.0.0', port=5000, debug=True)