"""
Course: CSE 251
Lesson Week: 11
File: Assignment.py
"""

from multiprocessing import process
from multiprocessing.context import Process
import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

# -----------------------------------------------------------------------------
def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

# -----------------------------------------------------------------------------
def cleaner_cleaning(id):
    print(f'Cleaner {id}')
    time.sleep(random.uniform(0, 2))

# -----------------------------------------------------------------------------
def guest_waiting():
    time.sleep(random.uniform(0, 2))

# -----------------------------------------------------------------------------
def guest_partying(id):
    print(f'Guest {id}')
    time.sleep(random.uniform(0, 1))

# -----------------------------------------------------------------------------
def cleaner(pid, end_time, clean_lock, cleaned_count):
    """
    do the following for TIME seconds
    cleaner will wait to try to clean the room (cleaner_waiting())
    get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    while end_time > time.time():
        
        # wait
        cleaner_waiting()

        # get access
        with clean_lock:
            print(STARTING_CLEANING_MESSAGE)

            # do cleaning etc.
            cleaner_cleaning(pid)
            print(STOPPING_CLEANING_MESSAGE)

        # count parties
        with cleaned_count.get_lock():
            cleaned_count.value += 1

# -----------------------------------------------------------------------------
def guest(pid, end_time, clean_lock, party_count, party_lock, waiting_count):
    """
    do the following for TIME seconds
    guest will wait to try to get access to the room (guest_waiting())
    get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    while end_time > time.time():
        guest_waiting()

        # get access to the room and assign who turns on the light
        with waiting_count.get_lock():
            light_on_duty = waiting_count.value == 0
            waiting_count.value += 1
        
        # turn on the lights
        # one person fits through the door at a time
        # avoids polling
        with party_lock:
            if light_on_duty:
                clean_lock.acquire()
                print(STARTING_PARTY_MESSAGE)

        # party hard
        guest_partying(pid)

        # leave the party and assign who turns off the light
        with waiting_count.get_lock():
            waiting_count.value -= 1
            light_off_duty = waiting_count.value == 0
        
        # turn off the lights
        # let the cleaners in
        if light_off_duty:
            print(STOPPING_PARTY_MESSAGE)
            clean_lock.release()
            
            # count parties
            with party_count.get_lock():
                party_count.value += 1

# -----------------------------------------------------------------------------
def main():
    # TODO - add any variables, data structures, processes you need
    waiting_count = mp.Value("i", 0)
    cleaned_count = mp.Value("i", 0)
    party_count = mp.Value("i", 0)
    clean_lock = mp.Lock()
    party_lock = mp.Lock()
    people: list[Process] = []

    # Start time of the running of the program. 
    start_time = time.time()
    end_time = start_time + TIME

    # TODO - add any arguments to cleaner() and guest() that you need
    people.extend([mp.Process(target=cleaner, args=(i+1, end_time, clean_lock, cleaned_count)) for i in range(CLEANING_STAFF)])
    people.extend([mp.Process(target=guest,   args=(i+1, end_time, clean_lock, party_count, party_lock, waiting_count))   for i in range(HOTEL_GUESTS)])

    for p in people:
        p.start()
    
    for p in people:
        p.join()
    

    # Results
    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')


if __name__ == '__main__':
    main()

