import os

import requests
import json
# from dotenv import load_dotenv
# API Ninjas key:
# load_dotenv()
# API_KEY = os.getenv('API_KEY')

BASE_URL = "https://api.api-ninjas.com/v1/"


def fetches_book_data_via_GET(animal : str):
    request_URL = f"{BASE_URL}animals?name={animal}"
    headers = {"X-Api-Key": API_KEY}
    print("Making the following request", request_URL)
    try:
        animals = requests.get(request_URL, headers=headers, timeout=5)
    except Exception as e:
        print("Error: no timely answer received from API")
    print("Result of the request: ", end="")
    if "200" in animals:
        print("GET request successful!")
    animals = animals.json()
    return animals

def fetches_data_from_file(file_path : str, animal : str):
    if animal.lower() != "fox":
        return ""
    with open(file_path, "r") as handle:
        return json.load(handle)

def fetch_data(animal:str):
    #return fetches_data_from_file("animals_data.json", animal)
    return fetches_data_via_GET(animal)