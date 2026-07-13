import json
from flask import Flask, request, render_template, redirect, url_for, abort
import os
import data_fetcher as df
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
host="http://127.0.0.1"
port=5000
host_port=host + ":" + str(port)

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
def return_to_home(current_function, outcome:dict):
    all_books = ds.get_all_books_elements()
    print(type(all_books))
    for title, author_name, publication_year, cover_image, book_id in all_books:
        print(f"title: {title}, author: {author_name}, publication_year: {publication_year}, cover_image: {cover_image}")
    return render_template('home.html',
                           app_name=app_name,
                           host_port=host_port,
                           all_books=all_books,
                           current_function=current_function,
                           outcome=outcome
                           )

def return_to_authors_list(current_function, outcome:dict):
    all_authors = ds.get_all_authors_from_db()
    for author_id, name, olid_author, cover_img, birth_year, death_year in all_authors:
        print(f"author_id: {author_id}, name: {name}, olid_author: {olid_author}, cover_image: {cover_img}, birth_year: {birth_year}, death_year: {death_year}")
    return render_template('list_authors.html',
                           app_name=app_name,
                           host_port=host_port,
                           all_authors=all_authors,
                           current_function=current_function,
                           outcome = outcome
                           )
"""
Routes
-----------------------------------------------------------------------
"""
@app.route('/', methods=['GET'])
def home():
    outcome = {'result': 200, 'message': 'empty'}
    return return_to_home("Current books in MAGO Library", outcome)



@app.route('/add_book', methods=['POST','GET'])
def add_book():
    """
    Note: OLID = Open Library Identifier (the ID mechanism of open library for books, authors and cover images
    This route enables the user to add a new book. The adding of a new book typically occurs in 4 STEPS
    STEP 1: GET request
    The 1st time this route is accessed is when
    the user selects on the Add book menu item. This is a GET request and the user receives the
    add_book.html file
    STEP 2: 1st POST request
    The 2nd time this route is accessed is when the user filled in a title and submits it. This
    results the reception of a POST request with the "book_title" and author fulfilled. Upon reception 2 things
    will need to happen:
    1. The DB is checked to see if a similar title/author is already stored. If it is, the similar_books value is
    filled with the similar titles already stored in Book.
    In this is case, the add_book.html is prefilled with the list of similar_books. If the user selects
    a book from this list, the session is aborted.
    2. from data_fetcher, the fetch_book_info is called, with the title and author as search items.
    The call is made to open library to search for this title/author. A list of dicts with all relevant books
    is returned. The title/author/publishing_year are displayed in a drop-down list with the olid_book_id as value that
    will be returned for the selected book.  The user has now 2 options, either it selects a book from the list and press
    "add book" or clicks "Manually add books".
    STEP 3: 2nd POST request to add the selected book (and indirectly the author if needed)
    3. The user selected "add book" for the selected book:
    First, there is a check if the Author OLID idea is already stored, or if there is already an author with
    the same name.
    If there is, the author_ID of this author is returned. If not, this new author is stored in the DB.
    After this, the Book elements are compiled and constructed so that it can be stored via ORM in the DB.
    request
    :return:
    """
    # 1st REQUEST, a GET request
    if request.method == 'GET':
        logging.info("Adding Book Process STEP 1: GET request")
        return render_template('add_book.html',
                                possible_books=[],
                                saved_book_title="E.g. Secret of secrets",
                                saved_author_name="E.g. Dan Brown",
                                similar_books=[],
                                current_function="Add a new book",
                                book_not_found = False
                               )

    saved_book_title = request.form.get('saved_book_title', "")
    saved_author_name = request.form.get('saved_author_name', "")

    book_title = request.form.get('book_title',"")
    author_name = request.form.get('author_name', "")
    print(f"book_title  {book_title} saved_book_title, {saved_book_title}, saved_author_name, {saved_author_name}")

    # 2nd REQUEST, a POST request
    if len(saved_book_title) == 0 and len(book_title) != 0:
        logging.info("Adding Book Process STEP 2: 1st POST request")

        similar_stored_books = ds.check_book_title_already_in_db(book_title)
        # 2 Options here, either there are similar_stored_books or not.
        # If similar books are found in the DB, the user will receive an adjusted
        # add_book.html where it can either select an existing title, or a title from the
        # possible books found on the open library. If there are no similar_books found
        # The user will only receive the possible book selection
        try:
            possible_books = df.fetch_book_info(book_title, author_name)
        except df.BookFetchException as e:
            outcome = {'result': 200, 'message': f'Could not fetch book/author information due to an exception: \n{e}. \nTry again later.'}
            return return_to_home("Adding a new author", outcome=outcome)
        # possible_books contains a list of dictionaries with specific info
        # I.e. title, author, olid_book_id, ordernumber
        book_not_found = True
        if len(possible_books) != 0:
            book_not_found = False
        return render_template('add_book.html',
                               possible_books=possible_books,
                               saved_book_title=book_title,
                               saved_author_name=saved_author_name,
                               similar_books=similar_stored_books,
                               current_function="Add a new book",
                               book_not_found=book_not_found
                               )
    # STEP 3: 2nd POST request to add the selected book (and indirectly the author if needed)
    # Here there are 3 scenario's for this stage:
    # 1. The user selected 1 of the possible_books. In that case:
    #    a. Check if the author is already stored
    #    b. If not, create an Author object and store it in the DB
    #    c. Create a book object and store it in the DB
    # 2. The user changed the book_title or author_name. In that case, it should be treated like the STEP 2
    # 3. The user selected the manual storage option. In that case, the rout /manually_add_book is selected

    # The user changed the wanted book title (case 2)
    if len(book_title) != 0 or len(author_name) != 0:
        similar_stored_books = ds.check_book_title_already_in_db(book_title)
        try:
            possible_books = df.fetch_book_info(book_title, author_name)
        except df.BookFetchException as e:
            outcome = {'result': 200, 'message': f'Could not fetch book/author information due to an exception: \n{e}. \nTry again later.'}
            return return_to_home("Adding a new author", outcome=outcome)
        available_books = []
        for book, author_name in possible_books:
            my_dict=book.serialize()
            my_dict['author_name'] = author_name
            available_books.append(my_dict)

        book_not_found = True
        if len(possible_books) != 0:
            book_not_found = False
        return render_template('add_book.html',
                               possible_books=available_books,
                               saved_book_title=book_title,
                               saved_author_name=saved_author_name,
                               similar_books=similar_stored_books,
                               current_function="Add a new book",
                               book_not_found=book_not_found,
                               )

    sim_stored_book = request.form.get('sim_book_nr', "")
    if sim_stored_book != "": # This is case 3, the user selected one of the already stored books
        return redirect(url_for("home"))
    # 1. The user selected 1 of the possible_books from the available options
    try:
        books_string = request.form.get('possible_books', "")
        possible_books = json.loads(books_string)
        selected_olid_book = request.form.get('pos_book_id', "")
        outcome_message = ""
    except (TypeError, ValueError) as e:
        abort(500, description=f"Unexpected returned input provided by the add_book.html form . {e}")

    book_dict_to_store = {}
    author_id = -1
    for the_book in possible_books:
        try:
            if the_book['olid_book_id'] == selected_olid_book and selected_olid_book != "":
                book_dict_to_store = the_book
                author_olid = the_book.get('olid_author_id')[0]
                author_id_and_name = ds.check_author_already_in_db(the_book["title"], author_olid)
                if len(author_id_and_name) == 0:
                    new_author = df.fetch_new_author(author_olid)
                    if new_author is not None:
                        # Store author in the DB
                        db.session.add(new_author)
                        db.session.commit()
                        author_id = new_author.author_id
                        outcome_message += f"<p>Successfully added author {new_author.name}.</p>"
                else:
                    author_id, author_name = author_id_and_name[0] # If the author was already stored in the DB.
                break

                # Note, if author is already stored, nothing needs to be done. Only the author_id is returned.
        except KeyError as e:
            message="Internal Error: could not find the olid_author or olid_book."
            logging.info(message)
            abort(500, descripton=message)

    logging.info(f"This book is about to be stored: {book_dict_to_store}")
    outcome = {'result': 500, 'message' : "An internal error occurred. Could not store book"}
    if book_dict_to_store != {}:
        if author_id == -1:
            outcome = ("Could not find a related book. Please ensure to store an "
                       "author before adding the book.")
            return render_template("home.html", outcome=outcome)
        book_dict_to_store['author_id'] = author_id
        book_to_store = df.fetch_new_book(book_dict_to_store)
        db.session.add(book_to_store)
        db.session.commit()
        outcome_message += f"<p>Successfully added book {book_to_store.title}</p>"
        outcome = {'result': 200, 'message' : outcome_message}
    return return_to_home("Adding a book", outcome=outcome )

@app.route('/manually_add_book', methods=['POST','GET'])
def manually_add_book():
    # 1st REQUEST, a GET request
    if request.method == 'GET':
        authors=ds.get_all_authors_from_db()

        book_title = request.args.get('book_title', "")
        logging.info(f"Manually adding a book with GET request for title: {book_title}")

        return render_template('manually_add_book.html',
                               current_function="Manually add a new book",
                               saved_book_title=book_title,
                               authors=authors
                               )

    # A post message is received. Now store the data
    logging.info("Adding Book with POST request")
    try:
        author_id = int(request.form.get('author_id', "-1"))
        publication_year = request.form.get('publication_year', "0")
        if len(publication_year) != 0:
            publication_year = int(publication_year)

    except (ValueError) as e:
        abort(404, description=f"Please check your input. \nWrong values received "
                               f"for either/both author or publication year. \n{e}.")
    if author_id == -1:
        abort(404, description=f"No author_id received. Please select an author")
    title = request.form.get('book_title', "")
    cover_img=df.compile_img_url(request.form.get('cover_img', ""))
    if len(title) == "":
        abort(404, description="No title was selected")
    received_book = Book(
        title=title,
        publication_year=publication_year,
        author_id=author_id,
        isbn=request.form.get('isbn', ""),
        cover_img=cover_img,
        olid_book_id=""
    )
    logging.info(f"This book will be stored: {received_book}")
    db.session.add(received_book)
    db.session.commit()
    outcome = {'result': 200, 'message' : f'Successfully added book {received_book.title}'}
    return return_to_home("home.html", outcome=outcome )

@app.route('/update_book', methods=['GET'])
def update_book():
    try:
        received_book_id = int(request.args.get('book_id', "-1"))
    except ValueError as e:
        abort(500, description=e)

    if received_book_id == -1:
        abort(404, description=f"Book with id {received_book_id} not found")

    book_to_update = ds.get_one_book(received_book_id)
    authors = ds.get_all_authors_from_db()
    return render_template('update_book.html',
                           app_name=app_name,
                           host_port=host_port,
                           book_to_update=book_to_update,
                           current_function="Updating a book",
                           authors=authors
                           )

@app.route('/updated_book', methods=['POST'])
def updated_book():
    try:
        book_id = int(request.form['book_id'])
        updated_publication_year = int(request.form.get('book_publication_year', "0"))
        updated_author = request.form.get('author_id', "-1")
    except ValueError as e:
        abort(500, description=f"Updated failed due to : {e}")
    updated_title = request.form.get('book_title', "")
    updated_book_isbn = request.form.get('book_isbn', "")
    updated_olid_book_id = request.form.get('olid_book_id', "")
    updated_cover_image = request.form.get('cover_image', "")

    book_to_update = ds.get_one_book(book_id)
    if len(updated_title) != 0:
        book_to_update.title = updated_title
    if len(updated_book_isbn) != 0:
        book_to_update.isbn = updated_book_isbn
    if updated_publication_year != 0:
        book_to_update.publication_year = updated_publication_year
    if len(updated_olid_book_id) != 0:
        book_to_update.olid_book_id = updated_olid_book_id
    if len(updated_cover_image) != 0:
        book_to_update.cover_img = df.compile_img_url(updated_cover_image, True)
    if updated_author != "Open to select author" and updated_author != "-1":
        book_to_update.author_id = updated_author

    db.session.commit()
    outcome = {'result': 200, 'message' : f'Update of book: id-{book_id} successful'}
    return return_to_home("Update a book", outcome)


@app.route('/delete_book', methods=['GET'])
def delete_book():
    try:
        received_book_id = int(request.args.get('book_id', "-1"))
    except ValueError as e:
        abort(500, description=e)

    if received_book_id == -1:
        abort(404, description=f"Book with id {received_book_id} not found")

    book_to_delete = ds.get_one_book(received_book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    outcome = {'result': 200, 'message' : f'Deletion of book: id-{received_book_id} successful'}
    return return_to_home("Delete a book", outcome)


@app.route('/list_authors', methods=['GET'])
def list_authors():
    all_authors = ds.get_all_authors_from_db()
    for author_id, name, olid_author, cover_img, birth_year, death_year in all_authors:
        print(f"author_id: {author_id}, name: {name}, olid_author: {olid_author}, cover_image: {cover_img}, birth_year: {birth_year}, death_year: {death_year}")
    return render_template('list_authors.html',
                           app_name=app_name,
                           host_port=host_port,
                           all_authors=all_authors,
                           current_function="Listing all authors"
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
        similar_stored_authors = ds.check_author_already_in_db(author_name)
        # 2 Options here, either there are similar_stored_authors or not.
        # If similar authors are found in the DB, the user will receive an adjusted
        # add_author.html where it can either select an existing name, or a name from the
        # possible authors found on the open library. If there are no similar_authors found
        # The user will only receive the possible author selection

        possible_authors = df.fetch_author_info(author_name)
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
        similar_stored_authors = ds.check_author_already_in_db(author_name)
        possible_authors = df.fetch_author_info(author_name)
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
    except ValueError as e:
        abort(500, description=f"return input provided by the add_author.html form is not an integer. See message: {e}")

    received_author = Author(
        name=possible_authors[selected_author]['name'],
        birth_year=possible_authors[selected_author].get('birth_year',"-"),
        death_year=possible_authors[selected_author].get('death_year',"-"),
        olid_author=possible_authors[selected_author].get('olid_author',"")
    )
    logging.info(f"This author will be stored: {received_author}")
    db.session.add(received_author)
    db.session.commit()
    outcome = {'result': 200, 'message' : f'Successfully added author {received_author.name}'}
    return return_to_authors_list("Adding a new author", outcome=outcome )

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
        birth_year=request.form.get('birth_year',"-"),
        death_year=request.form.get('death_year',"-"),
        cover_img=df.compile_img_url(request.form.get("cover_img","")),
        olid_author=""
    )
    logging.info(f"This author will be stored: {received_author}")
    db.session.add(received_author)
    db.session.commit()
    outcome = {'result': 200, 'message' : f'Successfully added author {received_author.name}'}
    return return_to_authors_list("Manually adding an author", outcome=outcome )


@app.route('/update_author', methods=['GET'])
def update_author():
    try:
        received_author_id = int(request.args.get('author_id', "-1"))
    except ValueError as e:
        abort(500, description=e)

    if received_author_id == -1:
        abort(404, description=f"Book with id {received_author_id} not found")

    author_to_update = ds.get_one_author(received_author_id)
    return render_template('update_author.html',
                           app_name=app_name,
                           host_port=host_port,
                           author_to_update=author_to_update,
                           current_function="Updating an author"
                           )

@app.route('/updated_author', methods=['POST'])
def updated_author():
    try:
        author_id = int(request.form['author_id'])
        birth_year = request.form.get('birth_year', "0")
        death_year = request.form.get('death_year', "0")
        if birth_year != "":
            birth_year = int(birth_year)
        if death_year != "":
            death_year = int(death_year)
    except ValueError as e:
        abort(500, description=f"Updated failed due to : {e}")
    updated_name = request.form.get('author_name', "")
    updated_olid_author = request.form.get('olid_author', "")
    updated_cover_image = request.form.get('cover_image', "")

    author_to_update = ds.get_one_author(author_id)
    if len(updated_name) != 0:
        author_to_update.name = updated_name
    if len(updated_olid_author) != 0:
        author_to_update.olid_author = updated_olid_author
    if birth_year != 0:
        author_to_update.birth_year = birth_year
    if death_year != 0:
        author_to_update.death_year = death_year
    if len(updated_cover_image) != 0:
        author_to_update.cover_img = df.compile_img_url(updated_cover_image, False)
    db.session.commit()
    outcome = {'result': 200, 'message' : f'Update of author: id-{author_id} successful'}
    return return_to_authors_list("Update an author", outcome)


@app.route('/delete_author', methods=['GET'])
def delete_author():
    try:
        received_author_id = int(request.args.get('author_id', "-1"))
    except ValueError as e:
        abort(500, description=e)

    if received_author_id == -1:
        abort(404, description=f"Book with id {received_author_id} not found")

    author_to_delete = ds.get_one_author(received_author_id)
    books_to_delete = ds.get_all_books_from_author(received_author_id)
    outcome = {'result': 200, 'message' : f'Deleting of author: {author_to_delete.name}\n'}
    for book in books_to_delete:
        db.session.delete(book)
        outcome['message'] =  outcome['message'] + f'Deleted book: {book.title}\n'
    db.session.delete(author_to_delete)
    outcome['message'] = outcome['message'] + f'Deleted author: {author_to_delete.name}\n'
    db.session.commit()
    outcome['message'] = outcome['message'] + f'Deleted author: {author_to_delete.name}'
    return return_to_authors_list("Delete an author", outcome)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, message=e.description), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', code=404, message=e.description), 500

@app.errorhandler(400)
def page_not_found(e):
    return render_template('error.html', code=400, message=e.description), 400

app.run(host='0.0.0.0', port=5000, debug=True)