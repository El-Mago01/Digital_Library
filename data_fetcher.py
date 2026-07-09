import os
import requests
import json
# from dotenv import load_dotenv
# API Ninjas key:
# load_dotenv()
# API_KEY = os.getenv('API_KEY')

class BookFetchException(Exception):
    pass

BASE_IMG_URL = "https://covers.openlibrary.org/b/isbn/"
BASE_BOOK_INFO_URL = "https://openlibrary.org/search.json?title="
FIELDS = "fields=key,title,author_name,editions,editions.key,editions.title,editions.ebook_access,editions.language,isbn"
BASE_AUTHOR_INFO_URL = "https://openlibrary.org/search/authors.json?q="
TIMEOUTVALUE = 20
def fetch_book_cover(isbn:str)->str:
    """
    This book cover image fetcher, doesn't actually fetch the cover image.
    It will compile an image URI, based upon the ISBN and checks if this image indeed
    exists.
    :param isbn:
    :return:
    """
    cover_uri = BASE_IMG_URL + isbn + "-M.jpg"
    try:
        cover_img = requests.get(cover_uri, timeout=TIMEOUTVALUE)
    except Exception as e:
        print("Error: no timely answer received from Open Library API")
        raise BookFetchException("The request to check cover image timed out")
    if cover_img.status_code == 200:
        return cover_uri
    else:
        return "Book-cover image not found"

def author_matches(provided_author:str, open_lib_author:str)->bool:
    print(f"checking if provided author {provided_author}, matches with fetched author {open_lib_author}")
    prov_author_names = provided_author.split()
    for names in prov_author_names:
        if names.lower() not in open_lib_author.lower():
            return False
    return True

def fetch_author_info(user_provided_author:str)->list:
    """
    This function fetches
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
                author_dict['key'] = author_details.get('key',"")
                author_dict['birth_year'] = author_details.get('birth_date')
                author_dict['death_year'] = author_details.get('death_date')
                author_dict['death_year'] = author_details.get('top_work')
                author_dict['top_subjects'] = authors_found.get('top_subjects')
                candidate_authors.append(author_dict)
    print("We encountered this/these author(s): ", candidate_authors)
    return candidate_authors

def fetch_detailed_book_info(book_title: str, user_provided_author:str)->tuple:
    isbn="NOT YET IMPLEMENTED"
    cover_img_loc = "NOT YET IMPLEMENTED"
    author_found = False
    search_string = book_title.split()
    search_string = "+".join(search_string)
    request_URL1 = f"{BASE_BOOK_INFO_URL}q={search_string}&{FIELDS}"
    # headers = {"X-Api-Key": API_KEY}
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
    print(book_details['numFound'])
    if book_details.get('numFound', 0) > 0:
        for book_finding in book_details['docs']:
            print(book_finding)
            found_authors = book_finding.get('author_name',[])
            if len(found_authors):
                for author in found_authors:
                    if author_matches(user_provided_author, author):
                        print(f"Found the correct book:\n{book_finding.get('title',"")} - {author} ", end="")
                        isbn = book_finding.get('isbn',["No valid ISBN"])[0]
                        cover_img_loc = fetch_book_cover(isbn)
                        author_found = True
                        break
                    else:
                        print(f"NOT Found the correct book:\n{book_finding.get('title',"")}{book_finding.get('author_name',"")} ", end="")
                if author_found:
                    break
    print(book_details)
    print(type(book_details))
    print("Cover image:", cover_img_loc)
    return isbn, cover_img_loc

