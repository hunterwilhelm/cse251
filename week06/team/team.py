"""
Course: CSE 251
Lesson Week: 06
File: team.py
Author: Brother Comeau

Purpose: Team Activity

Instructions:

- Implement the process functions to copy a text file exactly using a pipe

After you can copy a text file word by word exactly
- Change the program to be faster (Still using the processes)

"""

import multiprocessing as mp
from multiprocessing import Value, Process
import filecmp
from multiprocessing.connection import Connection 

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

def sender(filename, parent_pipe):
    """ function to send messages to other end of pipe """
    '''
    open the file
    send all contents of the file over a pipe to the other process
    Note: you must break each line in the file into words and
          send those words through the pipe
    '''
    with open(filename, 'r') as f:
        for line in f.readlines():
            parent_pipe.send(line.split(" "))
        parent_pipe.send(None)




def receiver(filename, child_pipe: Connection, count):
    """ function to print the messages received from other end of pipe """
    ''' 
    open the file for writing
    receive all content through the shared pipe and write to the file
    Keep track of the number of items sent over the pipe
    '''
    
    f = open(filename, 'w')
    f.close()

    with open(filename, 'a') as f:
        while (words := child_pipe.recv()) is not None:
            count.value += len(words)
            contents = " ".join(words)
            f.write(contents)

def are_files_same(filename1, filename2):
    """ Return True if two files are the same """
    return filecmp.cmp(filename1, filename2, shallow = False) 


def copy_file(log, filename1, filename2):
    # TODO create a pipe 
    parent, child = mp.Pipe()
    
    # TODO create variable to count items sent over the pipe
    count = mp.Value('i', 0)

    # TODO create processes 
    processes = []
    processes.append(mp.Process(target=receiver, args=[filename2, child, count]))
    processes.append(mp.Process(target=sender, args=[filename1, parent]))

    log.start_timer()
    start_time = log.get_time()

    # TODO start processes 
    for p in processes:
        p.start()
    
    # TODO wait for processes to finish
    for p in processes:
        p.join()

    stop_time = log.get_time()
    
    elapsed_time = stop_time - start_time
    log.stop_timer(f'Total time to transfer content = {elapsed_time}: ')
    log.write(f'items / second = {count.value / elapsed_time}')

    if are_files_same(filename1, filename2):
        log.write(f'{filename1} - Files are the same')
    else:
        log.write(f'{filename1} - Files are different')


if __name__ == "__main__": 

    log = Log(show_terminal=True)

    copy_file(log, 'gettysburg.txt', 'gettysburg-copy.txt')
    
    # After you get the gettysburg.txt file working, uncomment this statement
    copy_file(log, 'bom.txt', 'bom-copy.txt')

