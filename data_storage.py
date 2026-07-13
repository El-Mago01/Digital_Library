from data_models import db, Author, Book
from sqlalchemy import func, or_

def get_all_authors_from_db()->list:
    stmt = db.select(Author).order_by(Author.name.asc())
    author_list = db.session.execute(stmt).scalars().all()
    authors = []
    for author in author_list:
        authors.append((author.author_id, author.name, author.olid_author,
                        author.cover_img, author.birth_year, author.death_year))
    print(authors)
    return authors


def get_authors_name_and_ids()->list:
    name_ids=[]
    stmt = db.select(Author).order_by(Author.name.asc())
    authors = db.session.execute(stmt).scalars().all()
    for author in authors:
        name_ids.append((author.name, author.author_id))
    return name_ids



def get_all_books_elements(direction:str="asc")->list:
    books=[]
    stmt = db.select(Book, Author).join(Author, Book.author_id == Author.author_id).order_by(Book.title.asc())
    books_and_authors = db.session.execute(stmt).all()
    for book, author in books_and_authors:
        print(f"{book.title} - {author.name}")
        books.append((book.title, author.name, book.publication_year, book.cover_img, book.book_id))
    return books

def get_all_books_from_db()->list:
    stmt = db.select(Book).order_by(Book.title.asc())
    book_list = db.execute(stmt).scalars().all()
    return book_list

def get_one_book(requested_book_id:int)->Book:
    stmt = db.select(Book).where(
        Book.book_id == requested_book_id
    )
    book = db.session.execute(stmt).scalars().all()
    print(book)
    return book[0]

def get_one_author(requested_author_id:int)->Author:
    stmt = db.select(Author).where(
        Author.author_id == requested_author_id
    )
    author = db.session.execute(stmt).scalars().all()
    print(author)
    return author[0]



def check_author_already_in_db(author_name:str, author_olid:str="")->list:
    sim_authors=[]
    if author_olid != "":
        stmt = db.select(Author).where(
            Author.olid_author == author_olid
        )
    else:
        author_name = author_name.strip()
        stmt = db.select(Author).where(
            func.lower(Author.name) == author_name.lower())
    if author_olid != "" and author_name != "":
        author_name = author_name.strip()
        stmt = db.select(Author).where(or_ (func.lower(Author.name) == author_name.lower(),
                                       Author.olid_author == author_olid))
    similar_authors = db.session.execute(stmt).scalars().all()
    for author in similar_authors:
        sim_authors.append((author.author_id, author.name))
    # print( list(enumerate(sim_authors)))
    return sim_authors

def get_all_books_from_author(author_id:int)->list:
    stmt = db.select(Book).where(
        Book.author_id == author_id
    )
    book_list = db.session.execute(stmt).scalars().all()
    return book_list


def check_book_title_already_in_db(book_title:str)->list:
    sim_books=[]
    book_title = book_title.strip()
    stmt = db.select(Book, Author).join(Author, Book.author_id == Author.author_id).where(
        func.lower(Book.title) == book_title.lower())
    similar_books = db.session.execute(stmt).all()
    print(f"Found the following similar books: {similar_books}")
    for book, author in similar_books:
        sim_books.append((book.title, author.name, book.publication_year))
    print( list(enumerate(sim_books)))
    return list(enumerate(sim_books))












