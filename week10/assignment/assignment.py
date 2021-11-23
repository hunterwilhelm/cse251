"""
Course: CSE 251
Lesson Week: 10
File: assignment.py
Author: Hunter Wilhelm

Claim 5

Purpose: assignment for week 10 - reader writer problem

Instructions:

- Review TODO comments

- writer: a process that will send numbers to the reader.  
  The values sent to the readers will be in consecutive order starting
  at value 1.  Each writer will use all of the sharedList buffer area
  (ie., BUFFER_SIZE memory positions)

- reader: a process that receive numbers sent by the writer.  The reader will
  accept values until indicated by the writer that there are no more values to
  process.  Display the numbers received by printing them to the console.

- Create 2 writer processes

- Create 2 reader processes

- You can use sleep() statements for any process.

- You are able (should) to use lock(s) and semaphores(s).  When using locks, you can't
  use the arguments "block=False" or "timeout".  Your goal is to make your
  program as parallel as you can.  Over use of lock(s) or lock(s) in the wrong
  place will slow down your code.

- You must use ShareableList between the two processes.  This shareable list
  will contain different "sections".  There can only be one shareable list used
  between your processes.
  1) BUFFER_SIZE number of positions for data transfer. This buffer area must
     act like a queue - First In First Out.
  2) current value used by writers for consecutive order of values to send
  3) Any indexes that the processes need to keep track of the data queue
  4) Any other values you need for the assignment

- Not allowed to use Queue(), Pipe(), List() or any other data structure.

- Not allowed to use Value() or Array() or any other shared data type from 
  the multiprocessing package.

Add any comments for me:



"""
from multiprocessing import process
import random
from multiprocessing.managers import SharedMemoryManager
import multiprocessing as mp
from time import sleep
import time

LIST_SIZE = 10 # buffer size was described to be the list size. let's be more specific
INDEX_CONTINUE = 0
INDEX_WRITE_COUNT = 1
INDEX_READ_COUNT = 2
INDEX_DATA_LENGTH = 3
INDEX_DATA_START = 4
MAX_DATA_LENGTH = LIST_SIZE - INDEX_DATA_START

def write(data, write_semaphore, read_semaphore, items_to_send):
  while True:
    write_semaphore.acquire()
    count = data[INDEX_WRITE_COUNT]
    if count >= items_to_send:
      break    
    data_length = min(MAX_DATA_LENGTH, items_to_send - count)
    data[INDEX_DATA_LENGTH] = data_length
    for i in range(data_length):
      data[INDEX_DATA_START + i] = count + i + 1
    data[INDEX_WRITE_COUNT] = count + data_length
    read_semaphore.release()
  
  data[INDEX_CONTINUE] = 0
  read_semaphore.release()




def read(data, write_semaphore, read_semaphore):
  while True:
    read_semaphore.acquire()
    if not data[INDEX_CONTINUE]:
      break
    data_length = data[INDEX_DATA_LENGTH]
    data[INDEX_READ_COUNT] += data_length
    nums = [data[i] for i in range(INDEX_DATA_START, INDEX_DATA_START+data_length)]
    write_semaphore.release()
    for n in nums:
      print(n)
    print()
  
  write_semaphore.release()

def main():

    # This is the number of values that the writer will send to the reader
    items_to_send = 100000
    # items_to_send = random.randint(1000, 10000)

    smm = SharedMemoryManager()
    smm.start()

    # TODO - Create a ShareableList to be used between the processes
    data = smm.ShareableList([0] * LIST_SIZE)
    data[INDEX_CONTINUE] = 1

    # TODO - Create any lock(s) or semaphore(s) that you feel you need
    write_semaphore = mp.Semaphore(1)
    read_semaphore = mp.Semaphore(0)

    # TODO - create reader and writer processes
    processes = []
    processes.extend([mp.Process(target=read, args=(data, write_semaphore, read_semaphore,)) for _ in range(2)])
    processes.extend([mp.Process(target=write, args=(data, write_semaphore, read_semaphore, items_to_send)) for _ in range(2)])

    # TODO - Start the processes and wait for them to finish
    for p in processes:
        p.start()

    for p in processes:
        p.join()

    print(f'{items_to_send} values sent')

    # TODO - Display the number of numbers/items received by the reader.
    #        Can not use "items_to_send", must be a value collected
    #        by the reader processes.
    print(f'{data[INDEX_READ_COUNT]} values received')

    smm.shutdown()


if __name__ == '__main__':
    t = time.perf_counter()
    main()
    elapsed_time = time.perf_counter() - t
    print(elapsed_time)
