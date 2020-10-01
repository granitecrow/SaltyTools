# TODO: create a user class that contains login credentials and stats
# TODO: log the result of the fight to the big database
# TODO: if we bet last round then update if we won or loss
# TODO: log the result of our betting to our database
# TODO: determine the wager for the fight
 
import os
import sys
import time
import random

import requests
import json
from enum import Enum
from bs4 import BeautifulSoup

#local imports
import authenticate
from placebet import *
import saltysite
import config
import saltydb

class player(Enum):
    P1 = 'player1'
    P2 = 'player2'


def main():
    # Login to SaltyBet
    #TODO: ask user for email and password
    session, request = authenticate.login(config.EMAIL, config.PASSWORD)

    site = saltysite.scrape(session, request)
    db = saltydb.Database('saltybet.sqlite3.bin')

    print("--------------------------------------")
    print("Let's GO!!!!!")
    print("Rank: ", site.get_USER_leaderboard_rank())
    print("Bet Streak: ", site.get_USER_bet_streak())
    print("Balance: ", site.get_USER_balance())


    prev_status, status = "None", "None"
    prev_balance = site.get_USER_balance()
    duration = 0
    placed_bet = False

    while(True):
        time.sleep(7)

        prev_status = status
        site.update()
        status = site.get_betting_status()

        #  Status can be open, locked, 1, 2 (the numbers denote player1 or player2 victory)
        if(prev_status != 'open' and status == 'open'):
            placed_bet = False
            print("--------------------------------------")
            if prev_balance < site.get_USER_balance():
                print("You win!")
            elif prev_balance > site.get_USER_balance():
                print("You lose!")
            else:
                print("No change")
            print("--------------------------------------")
            print("Betting is now open!")
            print("--------------------------------------")
            print("Match: ", site.get_player1_name() + " vs " + site.get_player2_name())
            print("--------------------------------------")

            player1stats = db.retrieve_fighter(site.get_player1_name())
            print(player1stats)
            player2stats = db.retrieve_fighter(site.get_player2_name())
            print(player2stats)


            if player1stats.get('win_ratio') > player2stats.get('win_ratio'):
                fighter = player.P1
                print("Betting on " + site.get_player1_name())
            else:
                fighter = player.P2
                print("Betting on " + site.get_player2_name())

            if "bracket" in site.get_remaining():
                if (site.get_USER_balance() > 10000):
                    wager = int(site.get_USER_balance() * 0.1)
                else:
                    wager = site.get_USER_balance()
            else:
                    wager = int(site.get_USER_balance() * 0.05)

            print("Betting $" + str(wager))

            (fighter, wager) = determinebet(player1stats, player2stats)
            placebet(session, fighter, wager)
            prev_balance = site.get_USER_balance()
            # capture the datetime
            placed_bet = True
        elif (prev_status == 'open' and status == 'locked'):
            print("--------------------------------------")
            print("The bets are in and the match is underway!")
            print(site.get_player1_name() + ": " + site.get_player1_wagers())
            print(site.get_player2_name() + ": " + site.get_player2_wagers())
            print("Remaining: ",site.get_remaining())
            duration = 0
        elif (prev_status != '1' and status == '1'):
            print("--------------------------------------")
            print(site.get_player1_name() + " wins!")
            print("--------------------------------------")
            print("Rank: ", site.get_USER_leaderboard_rank())
            print("Bet Streak: ", site.get_USER_bet_streak())
            print("Balance: ", site.get_USER_balance())

            db.insert_ranking(site.get_player1_name(), site.get_player2_name())

        elif (prev_status != '2' and status == '2'):
            print("--------------------------------------")
            print(site.get_player2_name() + " wins!")
            print("--------------------------------------")
            print("Rank: ", site.get_USER_leaderboard_rank())
            print("Bet Streak: ", site.get_USER_bet_streak())
            print("Balance: ", site.get_USER_balance())
            
            db.insert_ranking(site.get_player2_name(), site.get_player1_name())

if __name__ == '__main__':
    main()


