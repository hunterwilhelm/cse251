"""
------------------------------------------------------------------------------
Course: CSE 251
Lesson Week: 03
File: assignment.py
Author: Hunter Wilhelm

Purpose: Video Frame Processing

Instructions:

- Follow the instructions found in Canvas for this assignment
- No other packages or modules are allowed to be used in this assignment.
  Do not change any of the from and import statements.
- Only process the given MP4 files for this assignment

------------------------------------------------------------------------------
Claim: 5. Made it my own
"""

from matplotlib.pylab import plt  # load plot library
from PIL import Image
import numpy as np
import timeit
import multiprocessing as mp

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *


# 4 more than the number of cpu's on your computer
CPU_COUNT = mp.cpu_count() + 4

# TODO Your final video need to have 300 processed frames.  However, while you are
# testing your code, set this much lower
FRAME_COUNT = 300

RED = 0
GREEN = 1
BLUE = 2


def create_new_frame(image_file, green_file, process_file):
    """ Creates a new image file from image_file and green_file """

    # this print() statement is there to help see which frame is being processed
    print(f'{process_file[-7:-4]}', end=',', flush=True)

    image_img = Image.open(image_file)
    green_img = Image.open(green_file)

    # Make Numpy array
    np_img = np.array(green_img)

    # Mask pixels
    mask = (np_img[:, :, BLUE] < 120) & (
        np_img[:, :, GREEN] > 120) & (np_img[:, :, RED] < 120)

    # Create mask image
    mask_img = Image.fromarray((mask*255).astype(np.uint8))

    image_new = Image.composite(image_img, green_img, mask_img)
    image_new.save(process_file)


# TODO add any functions to need here

def single_file_processing(image_number: int):

    image_file = rf'elephant/image{image_number:03d}.png'
    green_file = rf'green/image{image_number:03d}.png'
    process_file = rf'processed/image{image_number:03d}.png'

    create_new_frame(image_file, green_file, process_file)


def process_all_files(image_count: int, process_count: int) -> float:
    assert image_count > 0
    assert process_count > 0

    all_frames = list(range(1, image_count + 1))

    start_time = timeit.default_timer()
    with mp.Pool(process_count) as p:
        # map those 2 process to the function func()
        # Python will call the function func() alternating items in the names list.
        # the two processes will run in parallel
        p.map(single_file_processing, all_frames)
    time_elapsed = timeit.default_timer() - start_time
    print(f'\nTime To Process all images = {time_elapsed}')
    return time_elapsed


if __name__ == '__main__':
    all_process_time = timeit.default_timer()
    log = Log(show_terminal=True)

    xaxis_cpus = []
    yaxis_times = []

    # TODO Process all frames trying 1 cpu, then 2, then 3, ... to CPU_COUNT
    #      add results to xaxis_cpus and yaxis_times
    for c in range(1, CPU_COUNT):
        time_elapsed = process_all_files(FRAME_COUNT, c)
        xaxis_cpus.append(c)
        yaxis_times.append(time_elapsed)

    # sample code: remove before submitting  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # process one frame #10
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    log.write(f'Total Time for ALL processing: {timeit.default_timer() - all_process_time}')

    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_cpus, yaxis_times, label=f'{FRAME_COUNT}')

    plt.title('CPU Core yaxis_times VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig(f'Plot for {FRAME_COUNT} frames.png')
    plt.show()
