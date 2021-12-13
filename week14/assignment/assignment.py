"""
Course: CSE 251
Lesson Week: 14
File: assignment.py
Author: Hunter Wilhelm
Purpose: Assignment 13 - Family Search

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family = Request_thread(f'{TOP_API_URL}/family/{id}')

Requesting an individual from the server:
person = Request_thread(f'{TOP_API_URL}/person/{id}')


You will lose 10% if you don't detail your part 1 
and part 2 code below

Describe how to speed up part 1

The children of each family are not important for the discovery of new families. 
So, we can put this functionality in a non-recursive thread. 
To further speed it up, we can look them up from the tree to see if they are already in the tree. If not, then we get them from the server and put them into the tree. 
Again all of this inside the threads.

The parents of each family *are* important for the discovery of new families. 
So, we can put this functionality in a *recursive* thread. 
To further speed it up, we can spawn a thread for each parent which will be looking for more parents all at the same time adding the parents and children in the above statement to speed it up.

Describe how to speed up part 2

Get all of the families at once by id with threads and put them in the tree
From the families, get all of the children at once by id with threads BUT DON'T JOIN UNTIL THE END and put them in the tree
(If the children are already in the tree, then use that data instead)
From the families, get all of the parents at once by id with threads and put them in the tree
JOIN ALL the children threads

10% Bonus to speed up part 3

Refactor part 2 to handle a different request factory
Call part 2 with the following request factory
Use a semaphore to control how many calls are happening at once by wrapping the request thread in a class that has a semaphore
Use a function that returns a function that has the semaphore in the scope so the class can be created over and over
This is called currying and the factory design patterns
The process should now be limited to 5 calls at a time

"""
import time
import threading
import multiprocessing as mp
import json
import random
from typing import List
import requests

# Include cse 251 common Python files - Dont change
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *


TOP_API_URL = 'http://127.0.0.1:8123'


# ----------------------------------------------------------------------------
# Do not change this class
class Person:

    def __init__(self, data):
        super().__init__()
        self.id = data['id']
        self.name = data['name']
        self.parents = data['parent_id']
        self.family = data['family_id']
        self.birth = data['birth']

    def __str__(self):
        output  = f'id        : {self.id}\n'
        output += f'name      : {self.name}\n'
        output += f'birth     : {self.birth}\n'
        output += f'parent id : {self.parents}\n'
        output += f'family id : {self.family}\n'
        return output

# ----------------------------------------------------------------------------
# Do not change this class
class Family:

    def __init__(self, id, data):
        super().__init__()
        self.id = data['id']
        self.husband = data['husband_id']
        self.wife = data['wife_id']
        self.children = data['children']

    def children_count(self):
        return len(self.children)

    def __str__(self):
        output  = f'id         : {self.id}\n'
        output += f'husband    : {self.husband}\n'
        output += f'wife       : {self.wife}\n'
        for id in self.children:
            output += f'  Child    : {id}\n'
        return output

# -----------------------------------------------------------------------------
# Do not change this class
class Tree:

    def __init__(self, start_family_id):
        super().__init__()
        self.people = {}
        self.families = {}
        self.start_family_id = start_family_id

    def add_person(self, person):
        if self.does_person_exist(person.id):
            print(f'ERROR: Person with ID = {person.id} Already exists in the tree')
        else:
            self.people[person.id] = person

    def add_family(self, family):
        if self.does_family_exist(family.id):
            print(f'ERROR: Family with ID = {family.id} Already exists in the tree')
        else:
            self.families[family.id] = family

    def get_person(self, id):
        if id in self.people:
            return self.people[id]
        else:
            return None

    def get_family(self, id):
        if id in self.families:
            return self.families[id]
        else:
            return None

    def get_person_count(self):
        return len(self.people)

    def get_family_count(self):
        return len(self.families)

    def does_person_exist(self, id):
        return id in self.people

    def does_family_exist(self, id):
        return id in self.families

    def display(self, log):
        log.write('*' * 60)
        log.write('Tree Display')
        for family_id in self.families:
            fam = self.families[family_id]

            log.write(f'Family id: {family_id}')

            # Husband
            husband = self.get_person(fam.husband)
            if husband == None:
                log.write(f'  Husband: None')
            else:
                log.write(f'  Husband: {husband.name}, {husband.birth}')

            # wife
            wife = self.get_person(fam.wife)
            if wife == None:
                log.write(f'  Wife: None')
            else:
                log.write(f'  Wife: {wife.name}, {wife.birth}')

            # Parents of Husband
            if husband == None:
                log.write(f'  Husband Parents: None')
            else:
                parent_fam_id = husband.parents
                if parent_fam_id in self.families:
                    parent_fam = self.get_family(parent_fam_id)
                    father = self.get_person(parent_fam.husband)
                    mother = self.get_person(parent_fam.wife)
                    log.write(f'  Husband Parents: {father.name} and {mother.name}')
                else:
                    log.write(f'  Husband Parents: None')

            # Parents of Wife
            if wife == None:
                log.write(f'  Wife Parents: None')
            else:
                parent_fam_id = wife.parents
                if parent_fam_id in self.families:
                    parent_fam = self.get_family(parent_fam_id)
                    father = self.get_person(parent_fam.husband)
                    mother = self.get_person(parent_fam.wife)
                    log.write(f'  Wife Parents: {father.name} and {mother.name}')
                else:
                    log.write(f'  Wife Parents: None')

            # children
            output = []
            for index, child_id in enumerate(fam.children):
                person = self.people[child_id]
                output.append(f'{person.name}')
            out_str = str(output).replace("'", '', 100)
            log.write(f'  Children: {out_str[1:-1]}')


    def _test_number_connected_to_start(self):
        # start with first family, how many connected to that family
        inds_seen = set()

        def _recurive(family_id):
            nonlocal inds_seen
            if family_id in self.families:
                # count people in this family
                fam = self.families[family_id]

                husband = self.get_person(fam.husband)
                if husband != None:
                    if husband.id not in inds_seen:
                        inds_seen.add(husband.id)
                    _recurive(husband.parents)
                
                wife = self.get_person(fam.wife)
                if wife != None:
                    if wife.id not in inds_seen:
                        inds_seen.add(wife.id)
                    _recurive(wife.parents)

                for child_id in fam.children:
                    if child_id not in inds_seen:
                        inds_seen.add(child_id)


        _recurive(self.start_family_id)
        return len(inds_seen)


    def _count_generations(self, family_id):
        max_gen = -1

        def _recurive_gen(id, gen):
            nonlocal max_gen
            if id in self.families:
                if max_gen < gen:
                    max_gen = gen

                fam = self.families[id]

                husband = self.get_person(fam.husband)
                if husband != None:
                    _recurive_gen(husband.parents, gen + 1)
                
                wife = self.get_person(fam.wife)
                if wife != None:
                    _recurive_gen(wife.parents, gen + 1)

        _recurive_gen(family_id, 0)
        return max_gen + 1

    def __str__(self):
        out = '\nTree Stats:\n'
        out += f'Number of people                    : {len(self.people)}\n'
        out += f'Number of families                  : {len(self.families)}\n'
        out += f'Max generations                     : {self._count_generations(self.start_family_id)}\n'
        out += f'People connected to starting family : {self._test_number_connected_to_start()}\n'
        return out


# ----------------------------------------------------------------------------
# Do not change
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
            print('RESPONSE = ', response.status_code)


def get_family_from_server(family_id) -> Family:
    family_request = Request_thread(f'{TOP_API_URL}/family/{family_id}')
    family_request.start()
    family_request.join()
    return Family(None, family_request.response)

def get_person_from_server(person_id) -> Person:
    person_request = Request_thread(f'{TOP_API_URL}/person/{person_id}')
    person_request.start()
    person_request.join()
    return Person(person_request.response)

def get_person_from_tree_or_server_and_add(person_id, tree: Tree) -> Person:
    person = tree.get_person(person_id)
    if person is None:
        person = get_person_from_server(person_id)
        tree.add_person(person)
    return person

def recur_with_parent_id(person_id, tree: Tree):
    person = get_person_from_tree_or_server_and_add(person_id, tree)
    depth_fs_pedigree(person.parents, tree)

# -----------------------------------------------------------------------------
# TODO - Change this function to speed it up.  Your goal is to create the complete
#        tree faster.
def depth_fs_pedigree(family_id, tree: Tree):
    if family_id == None:
        return

    print(f'Retrieving Family: {family_id}')

    """
    outline:

    request family information
    request Husband - add to tree (Note there might not a husband in the family)
    request wife - add to tree (Note there might not a wife in the family)
    request children - add them to tree
    recursive call on the husband
    recursive call on the wife
    """

    family = get_family_from_server(family_id)
    tree.add_family(family)
    
    parent_ids = filter(lambda x: x is not None, [family.husband, family.wife])
    children_ids = family.children
    
    threads = []
    for person_id in children_ids:
        thread = threading.Thread(target=get_person_from_tree_or_server_and_add, args=(person_id, tree))
        threads.append(thread)

    for parent_id in parent_ids:
        thread = threading.Thread(
            target=recur_with_parent_id,
            args=(parent_id, tree)
        )
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


# -----------------------------------------------------------------------------
# You must not change this function
def part1(log, start_id, generations):
    tree = Tree(start_id)

    req = Request_thread(f'{TOP_API_URL}/start/{generations}')
    req.start()
    req.join()

    log.start_timer('Depth-First')
    depth_fs_pedigree(start_id, tree)
    total_time = log.stop_timer()

    req = Request_thread(f'{TOP_API_URL}/end')
    req.start()
    req.join()

    tree.display(log)
    log.write(tree)
    log.write(f'total_time                   : {total_time}')
    log.write(f'People and families / second : {(tree.get_person_count()  + tree.get_family_count()) / total_time}')
    log.write('')
# -----------------------------------------------------------------------------

def put_families_all_at_once(family_ids, tree: Tree, thread_factory) -> List[Family]:
    families: List[Family] = []
    family_requests = [thread_factory(f'{TOP_API_URL}/family/{family_id}') for family_id in family_ids]
    for family_req in family_requests:
        family_req.start()
    for family_req in family_requests:
        family_req.join()
        family = Family(None, family_req.response)
        print(f'Retrieved Family: {family.id}')
        tree.add_family(family)
        families.append(family)
    return families

def get_ids_from_families(families: List[Family]) -> tuple:
    parent_ids = []
    for family in families:
        parent_ids.extend([family.husband, family.wife])
    valid_parent_ids = [parent_id for parent_id in parent_ids if parent_id is not None]

    all_child_ids = []
    for family in families:
        all_child_ids.extend(family.children)
    
    return (valid_parent_ids, all_child_ids)

def put_all_people_at_once(person_ids, tree: Tree, request_factory) -> List[Person]:
    people = []
    person_ids_to_request = []
    
    for person_id in person_ids:
        person = tree.get_person(person_id)
        if person is None:
            person_ids_to_request.append(person_id)
        else:
            people.append(person)
    
    requests = [request_factory(f'{TOP_API_URL}/person/{person_id}') for person_id in person_ids_to_request]
    for req in requests:
        req.start()
    for req in requests:
        req.join()
        person = Person(req.response)
        tree.add_person(person)
        people.append(person)
    return people

def build_tree_breadth_first_retrieval(start_id, tree, thread_factory):
    current_family_ids = [start_id]
    children_threads: List[threading.Thread] = []
    
    while len(current_family_ids):
        families = put_families_all_at_once(current_family_ids, tree, thread_factory)  
        (valid_parent_ids, all_child_ids) = get_ids_from_families(families)
        children_threads.append(threading.Thread(target=put_all_people_at_once, args=(all_child_ids, tree, thread_factory)))
        children_threads[-1].start()
        parents = put_all_people_at_once(valid_parent_ids, tree, thread_factory)
        current_family_ids = [parent.parents for parent in parents if parent.parents is not None]

    for children_thread in children_threads:
        children_thread.join()

def breadth_fs_pedigree(start_id, tree):
    # TODO - implement breadth first retrieval
    # This video might help understand BFS
    # https://www.youtube.com/watch?v=86g8jAQug04
    build_tree_breadth_first_retrieval(start_id, tree, Request_thread)
# -----------------------------------------------------------------------------
# You must not change this function
def part2(log, start_id, generations):
    tree = Tree(start_id)

    req = Request_thread(f'{TOP_API_URL}/start/{generations}')
    req.start()
    req.join()

    log.start_timer('Breadth-First')
    breadth_fs_pedigree(start_id, tree)
    total_time = log.stop_timer()

    req = Request_thread(f'{TOP_API_URL}/end')
    req.start()
    req.join()

    tree.display(log)
    log.write(tree)
    log.write(f'total_time      : {total_time}')
    log.write(f'People / second : {tree.get_person_count() / total_time}')
    log.write('')


# -----------------------------------------------------------------------------

class LimitedRequestThread(threading.Thread):
    def __init__(self, url, semaphore: threading.Semaphore):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.request = Request_thread(url)
        self.response = {}
        self.semaphore = semaphore

    def run(self):
        self.semaphore.acquire()
        self.request.start()
        self.request.join()
        self.response = self.request.response
        self.semaphore.release()

def limitedRequestThreadFactoryFactory(semaphore):
    return lambda url: LimitedRequestThread(url, semaphore)

def breadth_fs_pedigree_limit5(start_id, tree):
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    limitedRequestThreadFactory = limitedRequestThreadFactoryFactory(threading.Semaphore(5))
    build_tree_breadth_first_retrieval(start_id, tree, limitedRequestThreadFactory)

# -----------------------------------------------------------------------------
# You must not change this function
# The goal is to limit the number of threads in part2 to 5
def part3(log, start_id, generations):
    tree = Tree(start_id)

    req = Request_thread(f'{TOP_API_URL}/start/{generations}')
    req.start()
    req.join()

    log.start_timer('Breadth-First')
    breadth_fs_pedigree_limit5(start_id, tree)
    total_time = log.stop_timer()

    req = Request_thread(f'{TOP_API_URL}/end')
    req.start()
    req.join()

    tree.display(log)
    log.write(tree)
    log.write(f'total_time      : {total_time}')
    log.write(f'People / second : {tree.get_person_count() / total_time}')
    log.write('')


# -----------------------------------------------------------------------------
def main():
    log = Log(show_terminal=True, filename_log='assignment.log')

    # starting family
    req = Request_thread(TOP_API_URL)
    req.start()
    req.join()

    print(f'Starting Family id: {req.response["start_family_id"]}')
    start_id = req.response['start_family_id']

    part1(log, start_id, 6)
    part2(log, start_id, 6)
    part3(log, start_id, 6)


if __name__ == '__main__':
    main()

