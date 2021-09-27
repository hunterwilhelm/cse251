"""
------------------------------------------------------------------------------
Course: CSE 251 
Lesson Week: 02
File: assignment.py 
Author: Brother Comeau

Purpose: Retrieve Star Wars details from a website

Instructions:

- Review instructions in I-Lean for this assignment.

The call to TOP_API_URL will return the following Dictionary.  Do NOT have this
dictionary hard coded - use the API call to get this dictionary.  Then you can
use this dictionary to make other API calls for data.

{
   "people": "http://swapi.dev/api/people/", 
   "planets": "http://swapi.dev/api/planets/", 
   "films": "http://swapi.dev/api/films/",
   "species": "http://swapi.dev/api/species/", 
   "vehicles": "http://swapi.dev/api/vehicles/", 
   "starships": "http://swapi.dev/api/starships/"
}

------------------------------------------------------------------------------
"""

from datetime import datetime, timedelta
import requests
import json
import threading

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

# Const Values
TOP_API_URL = r'https://swapi.dev/api'

# Global Variables
call_count = 0


# TODO Add your threaded class definition here
class RetrieveJson(threading.Thread):
    def __init__(self, url, key=None):
        super().__init__()
        
        # Hacky, I know, but we talked 
        # about this after class
        # The constructor code is not threaded
        global call_count
        call_count += 1

        self.url = url
        self.key = key
    
    def run(self):
        try:
            self.results = self._retrieve_json(self.url)
        except AssertionError:
            self.results = None
    
    def _retrieve_json(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            print('Error in requesting url:', url)
            print('Expected status code 200. Got:', response.status_code)
            raise AssertionError
        return response.json()


# TODO Add any functions you need here


def retrieve_top_api_urls(url):
    thread = RetrieveJson(url)
    run_threads((thread,))
    return thread.results

def retrieve_details_on_film(urls, film_id):
    url = urls["films"] + str(film_id)
    thread = RetrieveJson(url)
    run_threads((thread,))
    return thread.results

def make_threads(details, TYPES):
    threads = []
    for type in TYPES:
        for url in details[type]:
            thread = RetrieveJson(url, type)
            threads.append(thread)
    return threads

def run_threads(threads):
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

def retrieve_data_from_threads(threads, TYPES):
    data = {t: [] for t in TYPES}
    for t in threads:
        data[t.key].append(t.results["name"])
    for t in TYPES:
        data[t] = sorted(data[t])
    return data

def display_data(log, details, data, TYPES):
    log.write("----------------------------------------")
    log.write("Title   : " + details["title"])
    log.write("Director: " + details["director"])
    log.write("Producer: " + details["producer"])
    log.write("Released: " + details["release_date"])
    log.write()
    for t in TYPES:
        log.write(t.capitalize() + ": " + str(len(data[t])))
        log.write(", ".join(data[t]) + ",")
        log.write()

def main():
    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from swapi.dev')
    
    TYPES = ["characters", "planets", "starships", "vehicles", "species"]

    # TODO Retrieve Top API urls
    urls = retrieve_top_api_urls(TOP_API_URL)

    # TODO Retrieve Details on film 6
    details = retrieve_details_on_film(urls, 6)
    threads = make_threads(details, TYPES)
    run_threads(threads)
    data = retrieve_data_from_threads(threads, TYPES)
    
    # TODO Display results
    display_data(log, details, data, TYPES)

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to swapi server')
    

if __name__ == "__main__":
    main()
