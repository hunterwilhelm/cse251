"""
Course: CSE 251
Lesson Week: 02 - Team Activity
File: team.py
Author: Brother Comeau

Purpose: Playing Card API calls

Instructions:

- Review instructions in I-Learn.

"""

from datetime import datetime, timedelta
import threading
import requests
import json

# Include cse 251 common Python files
import os, sys
sys.path.append('../../code')   # Do not change the path.
from cse251 import *

# TODO Create a class based on (threading.Thread) that will
# make the API call to request data from the website

class Request_thread(threading.Thread):
    # TODO - Add code to make an API call and return the results
    # https://realpython.com/python-requests/
    def __init__(self, url):
      super().__init__()
      self.url = url
      self.result = None

    def run(self):
      print(f"requesting... \"{self.url}\"")
      response = requests.get(self.url)

      # Check the status code to see if the request succeeded.
      if response.status_code == 200:
          data = response.json()
          if 'success' in data:
              if data['success'] == True:
                self.result = data
              else:
                  print('Error in requesting ID')
          else:
              print('Error in requesting ID')
      else:
          print('Error in requesting ID')

class Deck:
    def __init__(self, deck_id):
        self.id = deck_id
        self.reshuffle()
        # self.remaining = 52


    def reshuffle(self):
        # TODO - add call to reshuffle
        thread = Request_thread(f"http://deckofcardsapi.com/api/deck/{self.id}/shuffle/")
        thread.start()
        thread.join()
        data = thread.result
        self.remaining = data["remaining"]
        return data

    def draw_card(self):
        return draw_cards(1)[0]
      
    
    def draw_cards(self, count):
        # TODO add call to get a card
        thread = Request_thread(f"http://deckofcardsapi.com/api/deck/{self.id}/draw/?count={count}")
        thread.start()
        thread.join()
        data = thread.result
        self.remaining = data["remaining"]
        return thread.result["cards"]

    def cards_remaining(self):
        return self.remaining


    def draw_endless(self):
        if self.remaining <= 0:
            self.reshuffle()
        return self.draw_card()

    
    def draw_endless_fast(self, count=55):
        cards = []
        c = count
        while c > 0:
          if self.remaining <= 0:
              self.reshuffle()
          draw_count = min(self.remaining, c)
          c -= draw_count
          cards.extend(self.draw_cards(draw_count))
        return cards


if __name__ == '__main__':

    # TODO - run the program team_get_deck_id.py and insert
    #        the deck ID here.  You only need to run the 
    #        team_get_deck_id.py program once. You can have
    #        multiple decks if you need them

    # deck_id = 'jfhvqliho0kj'
    deck_id = 'cpiyqgo91hn5'
    # Testing Code >>>>>
    deck = Deck(deck_id)
    # for i in range(55):
    #     card = deck.draw_endless()
    #     print(i, card, flush=True)
    for b in range(2):
      for i in range(1):
          cards = deck.draw_endless_fast(55)
          # for c in cards:
            # print(c["code"])
          print(f"{len(cards)}cards")

    print()
    # <<<<<<<<<<<<<<<<<<
