from data_models import db, Author, Book
from sqlalchemy import func

def get_all_authors_from_db()->list:
    stmt = db.select(Author).order_by(Author.name.asc())
    author_list = db.execute(stmt).scalars().all()
    return author_list

def check_author_name_already_in_db(author_name:str)->list:
    sim_authors=[]
    author_name = author_name.strip()
    stmt = db.select(Author).where(
        func.lower(Author.name) == author_name.lower())
    similar_authors = db.session.execute(stmt).scalars().all()
    print(f"Found the following similar authors: {similar_authors}")
    for author in similar_authors:
        sim_authors.append(author.name)
    print( list(enumerate(sim_authors)))
    return list(enumerate(sim_authors))


def get_all_books_from_db()->list:
    stmt = db.select(Book).order_by(Book.title.asc())
    book_list = db.execute(stmt).scalars().all()
    return book_list


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




