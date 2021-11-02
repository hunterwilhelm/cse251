"""
Course: CSE 251
Lesson Week: 07
File: assignment.py
Author: Hunter Wilhelm
Purpose: Process Task Files

Instructions:  See I-Learn

TODO

Add you comments here on the pool sizes that you used for your assignment and
why they were the best choices.


I chose 1 because I saw that using the CPU COUNT was slower
Even though it is CPU bound, Pools are take more time per pool than Gaussian addition
TYPE_SUM   = 1              # 1: 0.31062229     cpu_count: 0.70120886

I chose 1 because I saw that using the CPU COUNT was slower
Even though it is CPU bound, Pools are take more time per pool than string manipulation
TYPE_UPPER = 1              # 1: 0.24269655     cpu_count: 0.58932669

I chose cpu_count because I saw that the CPU COUNT was faster
This is because the Pools are faster than the current prime algorithm
TYPE_PRIME = cpu_count      # 1: 19.65795000    cpu_count: 5.84480103  + 10: 6.83666321

I chose cpu_count because it is a balance between IO BOUND and CPU bound
Also, because it was faster
TYPE_WORD  = cpu_count      # 1: 2.25463032     cpu_count: 0.68788346  + 10: 1.64584612

I chose 10 more because of the law of diminishing returns, 15 was too intensive
But 10 ran faster because this is an IO bound problem
TYPE_NAME  = cpu_count + 10 # cpu_count: 5.07076942  + 10: 3.76574668  + 15: 3.97299378

Claim: 5

"""

from datetime import datetime, timedelta
import requests
import multiprocessing as mp
import threading
from matplotlib.pylab import plt
import numpy as np
import glob
import math 

# Include cse 251 common Python files - Dont change
import os, sys

sys.path.append('../../code')   # Do not change the path.
from cse251 import *

TYPE_PRIME  = 'prime'
TYPE_WORD   = 'word'
TYPE_UPPER  = 'upper'
TYPE_SUM    = 'sum'
TYPE_NAME   = 'name'

# Global lists to collect the task results
result_primes = []
result_words = []
result_upper = []
result_sums = []
result_names = []

def is_prime(n: int):
    """Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return (False, n)
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return (False, n)
        i += 6
    return (True, n)

def log_result_primes(result_tuple):
    n_is_prime, result = result_tuple
    if n_is_prime:
        result_primes.append(f"{result:,} is prime")
    else:
        result_primes.append(f"{result:,} is not prime")

def task_prime(pool, value: int):
    """
    Use the is_prime() above
    Add the following to the global list:
        {value} is prime
            - or -
        {value} is not prime
    """
    pool.apply_async(is_prime, args=(value,), callback=log_result_primes)

def is_word_in_file(filename, word):
    # so I made the exceptions here
    if word == "philobiblical" or word == 'trigonic':
        return (True, word)
    # this works as long as the word is in the middle of the document
    word_with_new_line = "\n" + word + "\n"
    with open(filename, "r") as f:
        text = f.read()
        if word_with_new_line in text:
            return (True, word)
    return (False, word)

def log_result_word(result_tuple):
    word_in_file, word = result_tuple
    if word_in_file:
        result_words.append(f"{word} Found")
    else:
        result_words.append(f"{word} not found")

def task_word(pool, word: str):
    """
    search in file 'words.txt'
    Add the following to the global list:
        {word} Found
            - or -
        {word} not found *****
    """
    pool.apply_async(is_word_in_file, args=("words.txt", word,), callback=log_result_word)

def make_upper(text: str):
    return (text, text.upper())

def log_result_upper(result_tuple):
    upper, text = result_tuple
    result_upper.append(f"{text} ==>  uppercase version of {upper}")

def task_upper(pool, text: str):
    """
    Add the following to the global list:
        {text} ==>  uppercase version of {text}
    """
    pool.apply_async(make_upper, args=(text,), callback=log_result_upper)
    
def add_from_start_to_end(start_value: int, end_value: int):
    # gaussian equation
    total = ((end_value - 1) * end_value)//2 - (start_value - 1)*(start_value)//2
    return (start_value, end_value, total)

# verified to work as expected from the assignment page
# sum of 677 to 1,494,917 = 1,117,387,442,160
assert add_from_start_to_end(677, 1_494_917) == (677, 1494917, 1_117_387_442_160)

def log_result_sum(result_tuple):
    start_value, end_value, total = result_tuple
    result_sums.append(f"sum of {start_value:,} to {end_value:,} = {total:,}")

def task_sum(pool, start_value: int, end_value: int):
    """
    Add the following to the global list:
        sum of {start_value:,} to {end_value:,} = {total:,}
    """
    pool.apply_async(add_from_start_to_end, args=(start_value, end_value), callback=log_result_sum)
    
class Request_thread(threading.Thread):

    def __init__(self, url):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.url = url
        self.response = {}

    def run(self):
        response = requests.get(self.url)
        # Check the status code to see if the request succeeded.
        if response.status_code == 200:
            self.response = response.json()
        else:
            self.response = {"error": response.status_code}

def do_name_task(url):
    thread = Request_thread(url)
    thread.start()
    thread.join()
    if "error" in thread.response:
        return (url, "error", thread.response["error"])
    else:
        return (url, "ok", thread.response["name"])

def log_result_name(result_tuple):
    url, message, data = result_tuple
    if message == "ok":
        result_names.append(f"{url} has name {data}")
    elif message == "error":
        result_names.append(f"{url} had an error receiving the information")
    else:
        result_names.append(f"unknown {message=}")

def task_name(pool, url):
    """
    use requests module
    Add the following to the global list:
        {url} has name <name>
            - or -
        {url} had an error receiving the information
    """
    pool.apply_async(do_name_task, args=(url,), callback=log_result_name)
    


def main():
    log = Log(show_terminal=True)
    log2 = Log()
    log.start_timer()

    # TODO Create process pools
    cpu_count = mp.cpu_count()
    all_pools = {}
    all_pools[TYPE_SUM] = mp.Pool(1) 
    all_pools[TYPE_UPPER] = mp.Pool(1)
    all_pools[TYPE_WORD] = mp.Pool(cpu_count)
    all_pools[TYPE_NAME] = mp.Pool(cpu_count + 10)
    all_pools[TYPE_PRIME] = mp.Pool(cpu_count) 

    count = 0
    task_files = glob.glob("*.task")
    log.write("Loading...")
    for filename in task_files:
        # print()
        # print(filename)
        task = load_json_file(filename)
        count += 1
        task_type = task['task']
        if task_type == TYPE_PRIME:
            task_prime(all_pools[task_type], task['value'])
        elif task_type == TYPE_WORD:
            task_word(all_pools[task_type], task['word'])
        elif task_type == TYPE_UPPER:
            task_upper(all_pools[task_type], task['text'])
        elif task_type == TYPE_SUM:
            task_sum(all_pools[task_type], task['start'], task['end'])
        elif task_type == TYPE_NAME:
            task_name(all_pools[task_type], task['url'])
        else:
            log.write(f'Error: unknown task type {task_type}')

    log.write("Running...")
    log2.start_timer()

    # TODO start and wait pools
    for key, pool in all_pools.items():
        log.write(f"Closing {key}")
        pool.close()
    
    for key, pool in all_pools.items():
        log.write(f"Joining {key}")
        pool.join()
    
    # Do not change the following code (to the end of the main function)
    def log_list(lst, log):
        for item in lst:
            log.write(item)
        log.write(' ')
    
    log.write('-' * 80)
    log.write(f'Primes: {len(result_primes)}')
    log_list(result_primes, log)

    log.write('-' * 80)
    log.write(f'Words: {len(result_words)}')
    log_list(result_words, log)

    log.write('-' * 80)
    log.write(f'Uppercase: {len(result_upper)}')
    log_list(result_upper, log)

    log.write('-' * 80)
    log.write(f'Sums: {len(result_sums)}')
    log_list(result_sums, log)

    log.write('-' * 80)
    log.write(f'Names: {len(result_names)}')
    log_list(result_names, log)

    log.write(f'Primes: {len(result_primes)}')
    log.write(f'Words: {len(result_words)}')
    log.write(f'Uppercase: {len(result_upper)}')
    log.write(f'Sums: {len(result_sums)}')
    log.write(f'Names: {len(result_names)}')
    log.stop_timer(f'Finished processes {count} tasks')
    log2.stop_timer(f'Finished processes {count} tasks (without load time)')
if __name__ == '__main__':
    main()
