"""
Course: CSE 251
Lesson Week: 05
File: team.py
Author: Brother Comeau

Purpose: Check for prime values

Instructions:

- You can't use thread/process pools
- Follow the graph in I-Learn 
- Start with PRIME_PROCESS_COUNT = 1, then once it works, increase it

"""
from queue import Queue
import time
import threading
import multiprocessing as mp
import random

#Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

PRIME_PROCESS_COUNT = 

def is_prime(n: int) -> bool:
    """Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# TODO create read_thread function
def read_thread(filename: str, prime_queue: mp.Queue):
    with open(filename, "r") as f:
        for l in f.readlines():
            l = l.strip()
            prime_queue.put(int(l))
    prime_queue.put(None)



# TODO create prime_process function
def prime_process(prime_queue: mp.Queue, primes: list):
    while True:
        n = prime_queue.get()
        if n is None:
            prime_queue.put(None)
            break
        if is_prime(n):
            primes.append(n)

def create_data_txt(filename):
    with open(filename, 'w') as f:
        for _ in range(1000):
            f.write(str(random.randint(10000000000, 100000000000000)) + '\n')


def main():
    """ Main function """

    filename = 'data.txt'

    # Once the data file is created, you can comment out this line
    if not os.path.exists(filename):
        create_data_txt(filename)

    log = Log(show_terminal=True)
    log.start_timer()

    # TODO Create shared data structures
    prime_queue = mp.Queue()
    primes = mp.Manager().list([])

    # TODO create reading thread
    reading_thread = threading.Thread(target=read_thread, args=[filename, prime_queue])

    # TODO create prime processes
    prime_processes = [mp.Process(target=prime_process, args=[prime_queue, primes]) for i in range(PRIME_PROCESS_COUNT)]

    # TODO Start them all
    for p in prime_processes:
        p.start()
    reading_thread.start()

    # TODO wait for them to complete
    for p in prime_processes:
        p.join()
    reading_thread.join()

    log.stop_timer(f'All primes have been found using {PRIME_PROCESS_COUNT} processes')

    # display the list of primes
    print(f'There are {len(primes)} found:')
    for prime in primes:
        print(prime)


if __name__ == '__main__':
    main()

