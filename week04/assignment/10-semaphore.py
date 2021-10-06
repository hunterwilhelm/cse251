import time
from threading import Semaphore, Thread
import random
THREADS = 20
SEMAPHORE_COUNT = 3

# creating instance
def display(semaphore, name):

    # calling acquire method
    semaphore.acquire()

    time.sleep(random.random() * 3)
    print(f'Thread-{name}', flush=True)

    # calling release method
    semaphore.release()

def main():
    sem = Semaphore(SEMAPHORE_COUNT)

    # creating multiple thread
    threads = [Thread(target=display, args=(sem, f'{x}')) for x in range(THREADS)]

    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    

main()