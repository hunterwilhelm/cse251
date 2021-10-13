"""
Course: CSE 251
Lesson Week: 05
File: assignment.py
Author: Hunter Wilhelm

Purpose: Assignment 05 - Factories and Dealers

Instructions:

- Read the comments in the following code.  
- Implement your code where the TODO comments are found.
- No global variables, all data must be passed to the objects.
- Only the included/imported packages are allowed.  
- Thread/process pools are not allowed
- You are not allowed to use the normal Python Queue object.  You must use Queue251.
- the shared queue between the threads that are used to hold the Car objects
  can not be greater than MAX_QUEUE_SIZE


Claim. 5.
"""

from datetime import datetime, timedelta
import time
import threading
import random

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

# Global Consts
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 5000

# NO GLOBAL VARIABLES!

class Car():
    """ This is the Car class that will be created by the factories """

    # Class Variables
    car_makes = ('Ford', 'Chevrolet', 'Dodge', 'Fiat', 'Volvo', 'Infiniti', 'Jeep', 'Subaru', 
                'Buick', 'Volkswagen', 'Chrysler', 'Smart', 'Nissan', 'Toyota', 'Lexus', 
                'Mitsubishi', 'Mazda', 'Hyundai', 'Kia', 'Acura', 'Honda')

    car_models = ('A1', 'M1', 'XOX', 'XL', 'XLS', 'XLE' ,'Super' ,'Tall' ,'Flat', 'Middle', 'Round',
                'A2', 'M1X', 'SE', 'SXE', 'MM', 'Charger', 'Grand', 'Viper', 'F150', 'Town', 'Ranger',
                'G35', 'Titan', 'M5', 'GX', 'Sport', 'RX')

    car_years = [i for i in range(1990, datetime.now().year)]

    def __init__(self):
        # Make a random car
        self.model = random.choice(Car.car_models)
        self.make = random.choice(Car.car_makes)
        self.year = random.choice(Car.car_years)

        # Sleep a little.  Last statement in this for loop - don't change
        time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))

        # Display the car that has was just created in the terminal
        self.display()
           
    def display(self):
        print(f'{self.make} {self.model}, {self.year}')


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []
        self.max_size = 0

    def get_max_size(self):
        return self.max_size

    def put(self, item):
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.max_size = len(self.items)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """
    def __init__(self,
                 pid: int,
                 factory_barrier: threading.Barrier,
                 factory_spots: threading.Semaphore,
                 dealer_spots: threading.Semaphore,
                 car_queue: Queue251,
                 ):
        # TODO, you need to add arguments that will pass all of data that 1 factory needs
        # to create cars and to place them in a queue.
        self.pid = pid
        self.factory_barrier = factory_barrier
        self.factory_spots = factory_spots
        self.dealer_spots = dealer_spots
        self.car_queue = car_queue

        self.cars_to_produce = random.randint(200, 300)     # Don't change
        self.total_cars_made = 0
        super().__init__()

    def run(self):
        # TODO produce the cars, the send them to the dealerships
        for _ in range(self.cars_to_produce):
            self.factory_spots.acquire()
            car = Car()
            self.total_cars_made += 1
            self.car_queue.put(car)
            self.dealer_spots.release()
    
        # TODO wait until all of the factories are finished producing cars
        self.factory_barrier.wait()

        # TODO "Wake up/signal" the dealerships one more time.  Select one factory to do this
        if self.pid == 0:
            self.car_queue.put(None)
            self.dealer_spots.release()



class Dealer(threading.Thread):
    """ This is a dealer that receives cars """
    def __init__(self,
                 factory_spots: threading.Semaphore,
                 dealership_spots: threading.Semaphore, 
                 car_queue: Queue251, 
                 ):
        self.factory_spots = factory_spots
        self.dealership_spots = dealership_spots
        self.car_queue = car_queue

        self.total_cars_sold = 0
        super().__init__()

    def run(self):
        while True:
            # TODO handle a car
            self.dealership_spots.acquire()

            car = self.car_queue.get()
            if car is None:
                # if there are other threads, let them know too
                self.car_queue.put(None)
                self.dealership_spots.release()
                break

            self.total_cars_sold += 1

            self.factory_spots.release()

            # Sleep a little - don't change.  This is the last line of the loop
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR))



def run_production(factory_count, dealer_count):
    """ This function will do a production run with the number of
        factories and dealerships passed in as arguments.
    """

    # TODO Create semaphore(s)
    # TODO Create queue
    # TODO Create lock(s)
    # TODO Create barrier(s)
    
    factory_count = min(factory_count, MAX_QUEUE_SIZE) # prevent exceeding the queue

    factory_spots = threading.Semaphore(factory_count)
    factory_barrier = threading.Barrier(factory_count)
    dealership_spots = threading.Semaphore(0)
    car_queue = Queue251()

    # TODO create your factories, each factory will create CARS_TO_CREATE_PER_FACTORY
    factories: list[Factory] = []
    for i in range(factory_count):
        factories.append(Factory(i, factory_barrier, factory_spots, dealership_spots, car_queue))
    
    # TODO create your dealerships
    dealers: list[Dealer] = []
    print(f"{dealer_count=} {factory_count=}")
    for _ in range(dealer_count):
        dealers.append(Dealer(factory_spots, dealership_spots, car_queue))
    
    log.start_timer()

    # TODO Start all dealerships
    for t in dealers:
        t.start()

    time.sleep(1)   # make sure all dealers have time to start

    # TODO Start all factories
    for t in factories:
        t.start()

    # TODO Wait for factories and dealerships to complete
    for t in factories:
        t.join()
    for t in dealers:
        t.join()

    dealer_stats = [f.total_cars_sold for f in dealers]
    run_time = log.stop_timer(f'{sum(dealer_stats)} cars have been created')

    factory_stats = [f.total_cars_made for f in factories]

    # This function must return the following - Don't change!
    # factory_stats: is a list of the number of cars produced by each factory.
    #                collect this information after the factories are finished. 
    return (run_time, car_queue.get_max_size(), dealer_stats, factory_stats)


def main(log):
    """ Main function - DO NOT CHANGE! """

    runs = [(1, 1), (1, 2), (2, 1), (2, 2), (2, 5), (5, 2), (10, 10)]
    for factories, dealerships in runs:
        run_time, max_queue_size, dealer_stats, factory_stats = run_production(factories, dealerships)

        log.write(f'Factories      : {factories}')
        log.write(f'Dealerships    : {dealerships}')
        log.write(f'Run Time       : {run_time:.4f}')
        log.write(f'Max queue size : {max_queue_size}')
        log.write(f'Factory Stats  : {factory_stats}')
        log.write(f'Dealer Stats   : {dealer_stats}')
        log.write('')

        # The number of cars produces needs to match the cars sold
        assert sum(dealer_stats) == sum(factory_stats)


if __name__ == '__main__':

    log = Log(show_terminal=True)
    main(log)


