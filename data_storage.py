from data_models import db, Author, Book
from sqlalchemy import func, or_


def get_all_authors_from_db(direction: str = "asc") -> list:
    """
    returns all the available authors from the DB as a list of tuples with all available elements
    :param direction:
    :return:
    """
    if direction == "asc":
        stmt = db.select(Author).order_by(Author.name.asc())
    else:
        stmt = db.select(Author).order_by(Author.name.desc())
    author_list = db.session.execute(stmt).scalars().all()
    authors = []
    for author in author_list:
        authors.append(
            (
                author.author_id,
                author.name,
                author.olid_author,
                author.cover_img,
                author.birth_year,
                author.death_year,
            )
        )
    print(authors)
    return authors


def get_authors_name_and_ids() -> list:
    """
    returns all the authors from the DB as a list of tuples (name, author_id)
    :return:
    """
    name_ids = []
    stmt = db.select(Author).order_by(Author.name.asc())
    authors = db.session.execute(stmt).scalars().all()
    for author in authors:
        name_ids.append((author.name, author.author_id))
    return name_ids


def get_all_books_elements(sorting_command: dict) -> list:
    """
    return all most relevant available books elements, including author_name
    :param sorting_command:
    :return:
    """
    books = []
    if sorting_command["sort_by"] == "title":
        if sorting_command["direction"] == "asc":
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Book.title.asc())
            )
        else:
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Book.title.desc())
            )
    else:
        if sorting_command["direction"] == "asc":
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Author.name.asc())
            )
        else:
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Author.name.desc())
            )
    # stmt = db.select(Book, Author).join(Author, Book.author_id == Author.author_id).order_by(Author.name.asc())
    books_and_authors = db.session.execute(stmt).all()
    for book, author in books_and_authors:
        print(f"{book.title} - {author.name}")
        books.append(
            (
                book.title,
                author.name,
                book.publication_year,
                book.cover_img,
                book.book_id,
            )
        )
    return books


def get_all_books_from_db() -> list:
    """
    Returns all the available books in the DB. Note, this will NOT return the author name.
    If that is needed, use get_all_book_elements
    :return:
    """
    stmt = db.select(Book).order_by(Book.title.asc())
    book_list = db.execute(stmt).scalars().all()
    return book_list


def get_one_book(requested_book_id: int) -> Book:
    """
    Returns the book object related to the author_id
    :param requested_book_id:
    :return:
    """
    stmt = db.select(Book).where(Book.book_id == requested_book_id)
    book = db.session.execute(stmt).scalars().all()
    print(book)
    return book[0]


def get_one_author(requested_author_id: int) -> Author:
    """
    Returns the author object related to the author_id
    :param requested_author_id:
    :return:
    """
    stmt = db.select(Author).where(Author.author_id == requested_author_id)
    author = db.session.execute(stmt).scalars().all()
    print(author)
    return author[0]


def check_author_already_in_db(
        author_name: str,
        author_olid: str = "") -> list:
    """
    Checks if an author is already in the db. This search can be done using the open library identify or
    the own db identity
    :param author_name:
    :param author_olid:
    :return:
    """
    sim_authors = []
    if author_olid != "":
        stmt = db.select(Author).where(Author.olid_author == author_olid)
    else:
        author_name = author_name.strip()
        stmt = db.select(Author).where(
            func.lower(Author.name) == author_name.lower())
    if author_olid != "" and author_name != "":
        author_name = author_name.strip()
        stmt = db.select(Author).where(
            or_(
                func.lower(Author.name) == author_name.lower(),
                Author.olid_author == author_olid,
            )
        )
    similar_authors = db.session.execute(stmt).scalars().all()
    for author in similar_authors:
        sim_authors.append((author.author_id, author.name))
    # print( list(enumerate(sim_authors)))
    return sim_authors


def get_all_books_from_author(author_id: int) -> list:
    """
    returns all the available books from a specific author identified by author_id
    :param author_id:
    :return:
    """
    stmt = db.select(Book).where(Book.author_id == author_id)
    book_list = db.session.execute(stmt).scalars().all()
    return book_list


def check_book_title_already_in_db(book_title: str) -> list:
    """
    check if a book title is already in the db.
    :param book_title:
    :return:
    """
    sim_books = []
    book_title = book_title.strip()
    stmt = (
        db.select(Book, Author)
        .join(Author, Book.author_id == Author.author_id)
        .where(func.lower(Book.title) == book_title.lower())
    )
    similar_books = db.session.execute(stmt).all()
    print(f"Found the following similar books: {similar_books}")
    for book, author in similar_books:
        sim_books.append((book.title, author.name, book.publication_year))
    print(list(enumerate(sim_books)))
    return list(enumerate(sim_books))


def search_for_titles_and_authors(query: str, sorting_command):
    """
    Enables the search in the database using "%like%" SQL search, case-insensitive. The outcome is sored based
    upon user demands
    :param query: the searchstring
    :param sorting_command: user demands for sorting the output
    :return:
    """
    books = []
    query = "%" + query.strip().lower() + "%"
    if sorting_command["sort_by"] == "title":
        if sorting_command["direction"] == "asc":
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .where(
                    or_(
                        func.lower(Book.title.like(query)),
                        func.lower(Author.name.like(query)),
                    )
                )
                .order_by(Book.title.asc())
            )
        else:
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Book.title.desc())
            )
    else:
        if sorting_command["direction"] == "asc":
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Author.name.asc())
            )
        else:
            stmt = (
                db.select(Book, Author)
                .join(Author, Book.author_id == Author.author_id)
                .order_by(Author.name.desc())
            )
    # stmt = db.select(Book, Author).join(Author, Book.author_id == Author.author_id).order_by(Author.name.asc())
    books_and_authors = db.session.execute(stmt).all()
    for book, author in books_and_authors:
        print(f"{book.title} - {author.name}")
        books.append(
            (
                book.title,
                author.name,
                book.publication_year,
                book.cover_img,
                book.book_id,
            )
        )
    return books
