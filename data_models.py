# from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import logging

logging.basicConfig (
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)
#Create a db Object
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    olid_author = db.Column(db.String) # This is a reference key from open library
    cover_img = db.Column(db.String)
    birth_year = db.Column(db.String)
    death_year = db.Column(db.String)

    def __repr__(self):
        logging.info(f"Author: {self.name} author_id: {self.author_id} birth_year: {self.birth_year} death_year: {self.death_year}")
        return f"Author: {self.name} author_id: {self.author_id} birth_year: {self.birth_year} death_year: {self.death_year}"

    def __str__(self):
        return f"Author: {self.name} author_id: {self.author_id} birth_year: {self.birth_year} death_year: {self.death_year}"

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    olid_book_id = db.Column(db.Integer)
    olid_author_id = db.Column(db.String)
    isbn = db.Column(db.String)
    title = db.Column(db.String)
    cover_img = db.Column(db.String)
    author_id=db.Column(db.Integer, db.ForeignKey('authors.author_id'))
    publication_year = db.Column(db.Integer)

    def serialize(self):
        self_dict = {}
        self_dict['book_id'] = self.book_id
        self_dict['olid_book_id'] = self.olid_book_id
        self_dict['olid_author_id'] = self.olid_author_id
        self_dict['isbn'] = self.isbn
        self_dict['title'] = self.title
        self_dict['cover_img'] = self.cover_img
        self_dict['author_id'] = self.author_id
        self_dict['publication_year'] = self.publication_year
        return self_dict

    def __repr__(self):
        logging.info(f"Book title: {self.title} author_id: {self.author_id} publication_year: {self.publication_year}")
        return f"Book title: {self.title} author_id: {self.author_id} publication_year: {self.publication_year}"

    def __str__(self):
        return f"DEBUG: Book title: {self.title} author_id: {self.author_id} publication_year: {self.publication_year}"

