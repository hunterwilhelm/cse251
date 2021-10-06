"""
Course: CSE 251
Lesson Week: 04
File: team.py
Author: Brother Comeau

Purpose: Team Activity

Instructions:

- See in I-Learn

"""

import threading
import queue
import requests

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

RETRIEVE_THREADS = 4        # Number of retrieve_threads
NO_MORE_VALUES = 'No more'  # Special value to indicate no more items in the queue

def retrieve_thread(log, shared_queue):  # TODO add arguments
    """ Process values from the data_queue """

    while True:
        # TODO check to see if anything is in the queue
        url = shared_queue.get()
        # TODO process the value retrieved from the queue
        if url == NO_MORE_VALUES:
            shared_queue.put(NO_MORE_VALUES)
            break
        # TODO make Internet call to get characters name and log it
        response = requests.get(url)
        if response.status_code != 200:
            print('Error in requesting url:', url)
            print('Expected status code 200. Got:', response.status_code)
            raise AssertionError
        data = response.json()
        log.write(data["name"])



def file_reader(log, shared_queue): # TODO add arguments
    """ This thread reading the data file and places the values in the data_queue """

    # TODO Open the data file "data.txt" and place items into a queue
    with open("data.txt", "r") as f:
        lines = f.readlines()
        for l in lines:
            url = l.strip()
            shared_queue.put(url)

    log.write('finished reading file')

    # TODO signal the retrieve threads one more time that there are "no more values"
    shared_queue.put(NO_MORE_VALUES)



def main():
    """ Main function """

    log = Log(show_terminal=True)

    # TODO create queue
    shared_queue = queue.Queue()
    # TODO create semaphore (if needed)
    
    # TODO create the threads. 1 filereader() and RETRIEVE_THREADS retrieve_thread()s
    # Pass any arguments to these thread need to do their job
    file_thread = threading.Thread(target=file_reader, args=[log, shared_queue])
    retrieve_threads = [threading.Thread(target=retrieve_thread, args=[log, shared_queue]) for _ in range(RETRIEVE_THREADS)]


    log.start_timer()

    # TODO Get them going - start the retrieve_threads first, then file_reader

    file_thread.start()
    for t in retrieve_threads:
        t.start()
    
    # TODO Wait for them to finish - The order doesn't matter
    file_thread.join()
    for t in retrieve_threads:
        t.join()
    
    log.stop_timer('Time to process all URLS')


if __name__ == '__main__':
    main()




