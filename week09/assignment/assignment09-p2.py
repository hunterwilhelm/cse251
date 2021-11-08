"""
Course: CSE 251 
Lesson Week: 09
File: assignment09-p2.py 
Author: <Add name here>

Purpose: Part 2 of assignment 09, finding the end position in the maze

Instructions:
- Do not create classes for this assignment, just functions
- Do not use any other Python modules other than the ones included
- Each thread requires a different color by calling get_color()


This code is not interested in finding a path to the end position,
However, once you have completed this program, describe how you could 
change the program to display the found path to the exit position.

What would be your strategy?  

<Answer here>


Why would it work?

<Answer here>

"""
import math
import threading 
from screen import Screen
from maze import Maze, COLOR_VISITED

import cv2

# Include cse 251 common Python files - Dont change
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)

# Globals
current_color_index = 0
thread_count = 0
stop = False

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color

def solve_find_end(maze: Maze) -> tuple:
    """ finds the end position using threads.  Nothing is returned """
    # When one of the threads finds the end position, stop all of them
    global thread_count
    thread_count = 0

    thread_count_list: list[int] = []
    threads: list[threading.Thread] = []
    ends = []
    color_lock = threading.Lock()

    def recur(row: int, col: int, color: tuple):
        # stop the thread if the end is found
        if len(ends) > 0:
            return

        # Checking the pixel and then updating is
        # far from atomic. A lock is suggested in
        # theory to prevent race conditions on the
        # list's data
        with color_lock:
            # not thread safe
            if maze.can_move_here(row, col):
                maze.move(row, col, color)
    
        # destination
        if maze.at_end(row, col):
            ends.append((row, col)) # thread safe
            return

        moves = maze.get_possible_moves(row, col)
        valid_moves = list(filter(lambda p: maze.can_move_here(*p), moves))

        if len(valid_moves) > 0:
            # don't make a thread for the first one
            recur(*valid_moves.pop(), color)
            # for the rest, make threads
            thread_count_list.append(len(valid_moves))
            for pos in valid_moves:
                t = threading.Thread(target=recur, args=(*pos, get_color()))
                t.start()
                threads.append(t) # thread safe
    row, col = maze.get_start_pos()
    if maze.can_move_here(row, col):
        recur(row, col, COLOR_VISITED)
        for t in threads:
            t.join()
    
    thread_count += sum(thread_count_list)

    if len(ends) > 0:
        return ends[0]
    else:
        print("Could not find end")



def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    speed = 1
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('+'):
                speed = max(0, speed - 1)
            elif key == ord('-'):
                speed += 1
            elif key != ord('p'):
                done = True
        else:
            done = True



def find_ends(log):
    """ Do not change this function """

    files = (
        ('verysmall.bmp', True),
        ('verysmall-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)



if __name__ == "__main__":
    main()