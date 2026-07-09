import json
from flask import Flask, request, render_template, redirect, url_for, abort
import os
from data_fetcher import fetch_detailed_book_info, BookFetchException, fetch_author_info
import data_storage as ds
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


"""
Routes
-----------------------------------------------------------------------
"""
@app.route('/', methods=['GET'])
def home():

    all_books = ds.get_all_books_and_authors()
    print(type(all_books))
    for book in all_books:
        book_details=fetch_detailed_book_info(book[0], book[1])

        print(type(book))
    return render_template('home.html',
                           app_name=app_name,
                           all_books=all_books,
                           current_function="Current books in MAGO Library",
                           )


@app.route('/add_author', methods=['POST','GET'])
def add_author():
    """
    This route enables the user to add a new author. The 1st time this route is accessed is when
    the user selects on the Add Author menu item. This is a GET request and the user receives the
    add_author.html file without any data prefilled
    The 2nd time this route is accessed is when the user filled in a name and submits it. This
    results the reception of a POST request with the "author_name" fulfilled. Upon reception 3 things
    will need to happen:
    1. The DB is checked to see if a similar name is already stored. If it is, the similar_authors value is
    filled with the similar names already stored in Author.
    If this is the case, the add_author.html is prefilled with the list of similar_authors and the author_name
    is stored in save_author_name and forwarded to a hidden field
    saved_author_name
    2.
    request
    :return:
    """
    # 1st REQUEST, a GET request
    if request.method == 'GET':
        logging.info("Adding Author with GET request")
        return render_template('add_author.html',
                                possible_authors=[],
                                saved_author_name="",
                                similar_authors=[],
                                current_function="Add a new author",
                                author_not_found = False
                               )

    logging.info("Adding Author with POST request")
    saved_author_name = request.form.get('saved_author_name', "")
    author_name = request.form.get('author_name',"")
    print("author_name", author_name)
    print("saved_author_name", saved_author_name)

    # 2nd REQUEST, a POST request
    if len(saved_author_name) == 0 and len(author_name) != 0:
        similar_stored_authors = ds.check_author_name_already_in_db(author_name)
        # 2 Options here, either there are similar_stored_authors or not.
        # If similar authors are found in the DB, the user will receive an adjusted
        # add_author.html where it can either select an existing name, or a name from the
        # possible authors found on the open library. If there are no similar_authors found
        # The user will only receive the possible author selection

        possible_authors = fetch_author_info(author_name)
        author_not_found = True
        if len(possible_authors) != 0:
            author_not_found = False
        return render_template('add_author.html',
                               possible_authors=possible_authors,
                               saved_author_name=author_name,
                               similar_authors=similar_stored_authors,
                               current_function="Add a new author",
                               author_not_found=author_not_found
                               )
    # 3rd REQUEST, a POST request
    # Here there are 3 cases for entering this stage:
    # 1. The user selected 1 of the possible authors. In that case, store the selected author fields in the DB
    # 2. The user entered a new author_name. In that case, it should be handled as if the user entered in this stage
    #    is treated like it would be the 2nd REQUEST (POST)
    # 3. The user selected one of the already stored authors
    if len(author_name) != 0: # The user changed the wanted author name (case 2)
        similar_stored_authors = ds.check_author_name_already_in_db(author_name)
        possible_authors = fetch_author_info(author_name)
        author_not_found = True
        if len(possible_authors) != 0:
            author_not_found = False
        return render_template('add_author.html',
                               possible_authors=possible_authors,
                               saved_author_name=author_name,
                               similar_authors=similar_stored_authors,
                               current_function="Add a new author",
                               author_not_found=author_not_found
                               )
    sim_stored_author = request.form.get('sim_author_nr', "")
    if sim_stored_author != "": # This is case 3, the user selected one of the already stored authors
        return redirect(url_for("home"))

    try:
        # Case 1: The user selected one of the possible authors. Note, to finalize this, the possible authors need to be
        # "getted" from the hidden input field in add_author.html called possible_authors. Note. To enable storage of
        # a list, the list of possible authors from the 1st POST stage, is stored as json in this jinja2 variable
        authors_string = request.form.get('possible_authors', "")
        possible_authors = json.loads(authors_string)
        print("forwarded possible_authors: ", possible_authors)
        selected_author=int(request.form.get('pos_author_nr',-1))
        print("This is the final selected author", selected_author, possible_authors[selected_author]['name'])
    except:
        ValueError("Invalid return input provided by the add_author.html form")
        abort(500, description="return input provided by the add_author.html form is not an integer")
    received_author = Author(
        name=possible_authors[selected_author]['name'],
        birth_date=possible_authors[selected_author].get('birth_date',"-"),
        death_date=possible_authors[selected_author].get('death_date',"-"),
        key=possible_authors[selected_author].get('key',"")
    )
    logging.info(f"This author will be stored: {received_author}")
    db.session.add(received_author)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/manually_add_author', methods=['POST','GET'])
def manually_add_author():
    # 1st REQUEST, a GET request
    if request.method == 'GET':

        author_name = request.args.get('author_name', "")
        logging.info(f"Adding Author with GET request for name: {author_name}")

        return render_template('manually_add_author.html',
                               current_function="Manually add a new author",
                               saved_author_name=author_name
                               )
    # A post message is received. Now store the data
    logging.info("Adding Author with POST request")
    received_author = Author(
        name=request.form.get('author_name', ""),
        birth_date=request.form.get('birth_date',"-"),
        death_date=request.form.get('death_date',"-"),
        key=""
    )
    logging.info(f"This author will be stored: {received_author}")
    db.session.add(received_author)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/add_book', methods=['POST','GET'])
def add_book():
    if request.method == 'GET':
        authors=ds.get_authors_name_and_ids()

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', code=404, message=e.description), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', code=404, message=e.description), 500

@app.errorhandler(400)
def page_not_found(e):
    return render_template('400.html', code=400, message=e.description), 400

app.run(host='0.0.0.0', port=5000, debug=True)