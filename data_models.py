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
    birth_date = db.Column(db.String)
    death_date = db.Column(db.String)

    def __repr__(self):
        logging.info(f"Author: {self.name} author_id: {self.author_id} birth_date: {self.birth_date} death_date: {self.death_date}")
        return f"Author: {self.name} author_id: {self.author_id} birth_date: {self.birth_date} death_date: {self.death_date}"

    def __str__(self):
        return f"Author: {self.name} author_id: {self.author_id} birth_date: {self.birth_date} death_date: {self.death_date}"

class Book(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String)
    title = db.Column(db.String)
    author_id=db.Column(db.Integer, db.ForeignKey('authors.author_id'))
    publication_year = db.Column(db.Integer)

    def __repr__(self):
        logging.info(f"Book title: {self.title} author_id: {self.author_id} publication_year: {self.publication_year}")
        return f"Book title: {self.title} author_id: {self.author_id} publication_year: {self.publication_year}"

    def __str__(self):
        return f"DEBUG: Book title: {self.title} author_id: {self.author_id} publication_year: {self.publication_year}"

