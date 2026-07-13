import os
import requests
import json

from data_models import Book, Author
import logging
logging.basicConfig (
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

# from dotenv import load_dotenv
# API Ninjas key:
# load_dotenv()
# API_KEY = os.getenv('API_KEY')

class BookFetchException(Exception):
    pass

BASE_BOOK_INFO_URL = "https://openlibrary.org/search.json"
FIELDS = "fields=key,title,author_name,editions,editions.key,editions.title,editions.ebook_access,editions.language,isbn"
BASE_AUTHOR_INFO_URL = "https://openlibrary.org/search/authors.json?q="
SPECIFIC_BOOK_URL = "https://openlibrary.org/"
SPECIFIC_AUTHOR_URL = "https://openlibrary.org/authors/"
BOOK_IMAGE_URL = "https://covers.openlibrary.org/b/olid/"
AUTHOR_IMAGE_URL = "https://covers.openlibrary.org/a/olid/"
MAX_TITLE = 50
MAX_AUTHOR = 40

TIMEOUTVALUE = 20
def compile_img_url(olid:str, img_for_book:bool=True)->str:
    """
    This image url creator, doesn't actually fetch the cover image.
    It will compile an image URI, based upon the olid and checks if this image indeed
    exists.
    :param key: The olid for the book or author
    :param book: An indicator if the image is for a book or an author
    :return:
    """

    if img_for_book:
        # The case that the uri will be generated for an author image
        if "https" in olid:
            cover_uri = olid #This is the case if the user is changing the uri
        else:
            cover_uri = BOOK_IMAGE_URL + olid + "-M.jpg?default=false"
    else:
        # The case that the uri will be generated for an author image
        if "https" in olid:
            cover_uri = olid
        else:
            cover_uri = AUTHOR_IMAGE_URL + olid + "-M.jpg?default=false"
    try:
        cover_img = requests.get(cover_uri, timeout=TIMEOUTVALUE)
    except Exception as e:
        print("Error: no timely answer received from Open Library API")
        raise BookFetchException("The request to check cover image for author timed out")
    if cover_img.status_code == 200:
        return cover_uri
    else:
        return "Not Found"


# def author_matches(provided_author:str, open_lib_author:str)->bool:
#     print(f"checking if provided author {provided_author}, matches with fetched author {open_lib_author}")
#     prov_author_names = provided_author.split()
#     for names in prov_author_names:
#         if names.lower() not in open_lib_author.lower():
#             return False
#     return True

def fetch_author_info(user_provided_author:str)->list:
    """
    This function fetches all the relevant authors for the "add author" search query. As such, the
    information is enough to instantiate the Author object.
    :param user_provided_author:
    :return:
    """

    candidate_authors = []
    search_string = user_provided_author.split()
    search_string = "+".join(search_string)
    request_URL1 = f"{BASE_AUTHOR_INFO_URL}{search_string}"
    print("Making the following request:\n", request_URL1)
    try:
        author_info = requests.get(request_URL1, timeout=TIMEOUTVALUE)
    except Exception as e:
        print("Error: no timely answer received from API")
        raise BookFetchException("The request to get author information timed out")

    print("Result of the request: ", end="")
    if author_info.status_code == 200:
        print("GET request successful!")
    author_details = author_info.json()
    print("Number of authors found=", author_details.get('numFound', 0))
    if author_details.get('numFound', 0) > 0:
        candidate_authors = []
        order_number = 0
        for authors_found in author_details['docs']:
            print(authors_found, type(authors_found))
            found_author = authors_found.get('name',"")
            if len(found_author):
                author_dict={}
                author_dict['order_number'] = order_number
                order_number += 1
                author_dict['name'] = found_author
                author_dict['olid_author'] = author_details.get('key',"")
                author_dict['birth_year'] = author_details.get('birth_year')
                author_dict['death_year'] = author_details.get('death_year')
                author_dict['death_year'] = author_details.get('top_work')
                author_dict['cover_img'] = "Not Found"
                author_dict['top_subjects'] = authors_found.get('top_subjects')
                candidate_authors.append(author_dict)
    print("We encountered this/these author(s): ", candidate_authors)
    return candidate_authors

def fetch_year_from_input(date_string:str)->str:
    year_list = date_string.split()
    if len(year_list) == 3:
        year = year_list[2]
    else:
        year = year_list[0]
    return year

def fetch_new_author(author_olid: str)-> Author:
    request_URL1 = SPECIFIC_AUTHOR_URL + author_olid + ".json"
    print("Making the following request:\n", request_URL1)
    try:
        author_info = requests.get(request_URL1, timeout=TIMEOUTVALUE)
    except Exception as e:
        print("Error: no timely answer received from API")
        raise BookFetchException("The request to get author information timed out")

    print("Result of the request: ", end="")
    if author_info.status_code == 200:
        print("GET request successful!")
    author_details = author_info.json()

    new_author = Author(
        name=author_details.get('name', ""),
        cover_img=compile_img_url(author_olid, False),
        birth_year=fetch_year_from_input(author_details.get('birth_year', "- - -")),
        death_year=fetch_year_from_input(author_details.get('death_year', "- - -")),
        olid_author=author_olid
    )
    print(new_author)
    return new_author

def fetch_book_info(user_provided_book:str, user_provided_author_name:str)->list:
    """
    This function fetches
    :param user_provided_book:
    :param user_provided_author_name:
    :return:
    """

    candidate_books = []
    author_names = []

    search_string = ""
    if len(user_provided_book) > 0:
        search_string = "?title="
        split_string = user_provided_book.split()
        search_string += "+".join(split_string)
    if len(user_provided_author_name) > 0:
        author_string = user_provided_author_name.split()
        if len(search_string) > 0: #in this case, a title was provided
            search_string += "&author="
        else:
            search_string = "?author="
        search_string += "+".join(author_string)
    if len(search_string) == 0:
        raise BookFetchException("Both book title and author name are empty..")
    search_string += "&fields=*"

    request_URL1 = f"{BASE_BOOK_INFO_URL}{search_string}"
    print("Making the following request:\n", request_URL1)
    try:
        book_info = requests.get(request_URL1, timeout=TIMEOUTVALUE)
    except Exception as e:
        print("Error: no timely answer received from API")
        raise BookFetchException("The request to get book information timed out")

    print("Result of the request: ", end="")
    if book_info.status_code == 200:
        print("GET request successful!")
    book_details = book_info.json()
    print("Number of books found=", book_details.get('numFound', 0))
    if book_details.get('numFound', 0) > 0:
        for book_found in book_details['docs']:
            logging.info(f"Result of GET response with URL:\n{request_URL1}:\n{book_found}")
            found_book = book_found.get('title',"")
            if len(found_book):
                cover_key = book_found.get('cover_edition_key', "")
                new_book = Book(
                    olid_book_id = book_found.get('key', ""),
                    olid_author_id = book_found.get('author_key', ""),
                    isbn = book_found.get('isbn', [""])[0],
                    title = found_book.strip()[:MAX_TITLE],
                    cover_img = compile_img_url(cover_key, True),
                    author_id = -1,
                    publication_year = book_found.get('first_publish_year', ""),
                )
                author_name = book_found.get('author_name', [""])[0].strip()[:MAX_AUTHOR]
                candidate_books.append((new_book, author_name))
        print(f"We encountered this/these book(s) from open library from author{author_names}", candidate_books)
        return candidate_books
    return []

def fetch_new_book(selected_book: dict)->Book:
    book_to_store = Book(
        author_id=selected_book.get('author_id'),
        title=selected_book.get('title'),
        isbn=selected_book.get('isbn', "-"),
        cover_img=selected_book.get('cover_img', "-"),
        publication_year=selected_book.get('publication_year', "-"),
        olid_book_id=selected_book.get('olid_book_id',""),
        olid_author_id=selected_book.get('olid_author_id',"")[0]
    )
    return book_to_store




