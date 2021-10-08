"""
Course: CSE 251
Lesson Week: 04
File: assignment.py
Author: <Your name>

Purpose: Assignment 04 - Factory and Dealership

Instructions:

- See I-Learn

Claim: 5

"""

import time
import threading
import random

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

# Global Consts - Do not change
CARS_TO_PRODUCE = 500
MAX_QUEUE_SIZE = 10
SLEEP_REDUCE_FACTOR = 50

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

        # Display the car that has just be created in the terminal
        self.display()
           
    def display(self):
        print(f'{self.make} {self.model}, {self.year}')


class Queue251():
    """ This is the queue object to use for this assignment. Do not modify!! """

    def __init__(self):
        self.items = []

    def size(self):
        return len(self.items)

    def put(self, item):
        self.items.append(item)

    def get(self):
        return self.items.pop(0)


class Factory(threading.Thread):
    """ This is a factory.  It will create cars and place them on the car queue """

    def __init__(self,
                 shared_queue: Queue251,
                 factory_spots: threading.Semaphore,
                 dealer_spots: threading.Semaphore):
        # TODO, you need to add arguments that will pass all of data that 1 factory needs
        # to create cars and to place them in a queue.
        self.shared_queue = shared_queue
        self.factory_spots = factory_spots
        self.dealer_spots = dealer_spots
        super().__init__()


    def run(self):
        for _ in range(CARS_TO_PRODUCE):
            # TODO Add you code here
            """
            create a car
            place the car on the queue
            signal the dealer that there is a car on the queue
            """
            self.factory_spots.acquire()
            car = Car()
            self.shared_queue.put(car)
            self.dealer_spots.release()

        # signal the dealer that there there are not more cars
        self.factory_spots.acquire()
        self.shared_queue.put(None)
        self.dealer_spots.release()



class Dealer(threading.Thread):
    """ This is a dealer that receives cars """

    def __init__(self,
                 shared_queue: Queue251,
                 factory_spots: threading.Semaphore, 
                 dealership_spots: threading.Semaphore, 
                 queue_stats: threading.Semaphore):
        # TODO, you need to add arguments that pass all of data that 1 dealer needs
        # to sell cars and signal the factory that there is an empty slot in the queue
        self.shared_queue = shared_queue
        self.factory_spots = factory_spots
        self.dealership_spots = dealership_spots
        self.queue_stats = queue_stats
        super().__init__()

    def run(self):
        while True:
            # TODO Add your code here
            """
            take the car from the queue
            signal the factory that there is an empty slot in the queue
            """
            self.dealership_spots.acquire()
            stats_size_index = self.shared_queue.size() - 1
            # If we had more than 1 dealer, then we would need a lock here
            self.queue_stats[stats_size_index] += 1

            car = self.shared_queue.get()
            if car is None:
                # if there are other threads, let them know too
                self.shared_queue.put(None)
                break
            self.factory_spots.release()

            # Sleep a little after selling a car
            # Last statement in this for loop - don't change
            time.sleep(random.random() / (SLEEP_REDUCE_FACTOR) *)



def main():
    log = Log(show_terminal=True)

    # TODO Create semaphore(s)
    # TODO Create queue251 
    # TODO Create lock(s) ?
    factory_spots = threading.Semaphore(MAX_QUEUE_SIZE)
    dealership_spots = threading.Semaphore(0)
    shared_queue = Queue251()
    # If we had more than 1 dealer, then we would need a lock here

    # This tracks the length of the car queue during receiving cars by the dealership
    # i.e., update this list each time the dealer receives a car
    queue_stats = [0] * MAX_QUEUE_SIZE

    # TODO create your one factory
    factory = Factory(shared_queue, factory_spots, dealership_spots)

    # TODO create your one dealership
    dealership = Dealer(shared_queue, factory_spots, dealership_spots, queue_stats)

    log.start_timer()

    # TODO Start factory and dealership
    factory.start()
    dealership.start()

    # TODO Wait for factory and dealership to complete
    factory.join()
    dealership.join()

    log.stop_timer(f'All {sum(queue_stats)} have been created')

    xaxis = [i for i in range(1, MAX_QUEUE_SIZE + 1)]
    plot = Plots()
    plot.bar(xaxis, queue_stats, title=f'{sum(queue_stats)} Produced: Count VS Queue Size', x_label='Queue Size', y_label='Count')



if __name__ == '__main__':
    main()
