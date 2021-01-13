import os
import sys
import time
import random
import getpass

import requests
import json
from enum import Enum
from bs4 import BeautifulSoup

#local imports
import authenticate
from placebet import *
from consoledisplay import *
import saltysite
import config
import saltydb
from elo import *

class player(Enum):
    P1 = 'player1'
    P2 = 'player2'

def main():
    # Login to SaltyBet
    user = input("Email: ")
    pwd = getpass.getpass()
    session, request = authenticate.login(user, pwd)

    site = saltysite.scrape(session, request)
    db = saltydb.Database('saltybet.sqlite3.bin')
    print_welcome_message()
    print_user_stats(site.get_USER_leaderboard_rank(), site.get_USER_bet_streak(), site.get_USER_balance())

    prev_status, status = "None", "None"
    prev_balance = site.get_USER_balance()
    placed_bet = False

    # This dictionary will build a result.json file for historical checking
    Salty_Bet = dict()

    while(True):
        time.sleep(7)

        prev_status = status
       
        site.update()

        # I think this is what caused the DDOS attack
        #try:
        #    site.update()
        #except: #try again in case we receive connection refused errors
        #    session, request = authenticate.login(user, pwd)
        #    site = saltysite.scrape(session, request)
        
        status = site.get_betting_status()

        if(prev_status != status):
            user_balance = site.get_USER_balance()
            player1name = site.get_player1_name()
            player2name = site.get_player2_name()
            player1stats = db.retrieve_fighter(player1name)
            player2stats = db.retrieve_fighter(player2name)
            (Pa, Pb) = ExpectedProbabilities(player1stats.get('elo'), player2stats.get('elo'))

        #  Status can be open, locked, 1, 2 (the numbers denote player1 or player2 victory)
        if(prev_status != 'open' and status == 'open'):

            if(placed_bet):
                print_last_match_results(prev_balance, user_balance, placed_bet)
                changed = user_balance - prev_balance
                Salty_Bet.update({'Delta':changed})
                with open('result.json', 'a+') as fp:
                    json.dump(Salty_Bet, fp)
                    fp.write('\n')

            print_user_stats(site.get_USER_leaderboard_rank(), site.get_USER_bet_streak(), site.get_USER_balance())

            print_match_details(player1stats, player2stats, Pa, Pb)
            placed_bet = False

            isP1favored = Pa > Pb
            # simulate matches so that we select underdogs at same percentage of their win chance
            sim_game = random.randrange(0, 9999, 1) #hardcode 10000 matches; step of 1
            didP1win = sim_game < (Pa * 10000)
            if (didP1win == True and isP1favored == True):
                fighter = player.P1
                current_bet = player1stats['fighter']
                print(f"SIMULATING :: Taking the favorite with fighter {player1stats['fighter']}")
            elif (didP1win == True and isP1favored == False):
                fighter = player.P1
                current_bet = player1stats['fighter']
                print(f"SIMULATING :: Taking the underdog with fighter {player1stats['fighter']}")
            elif (didP1win == False and isP1favored == True):
                fighter = player.P2
                current_bet = player2stats['fighter']
                print(f"SIMULATING :: Taking the underdog with fighter {player2stats['fighter']}")
            else: #(didP1win == False & isP1favored == False):
                fighter = player.P2
                current_bet = player2stats['fighter']
                print(f"SIMULATING :: Taking the favorite with fighter {player2stats['fighter']}")

            # determine_wager - would be nice to put some real logic here some day!
            game_mode = site.get_match_type()
            if game_mode == "bracket":
                if (user_balance > 10000):
                    wager = int(user_balance * 0.1)
                else:
                    wager = user_balance
            elif game_mode == "exhibition":
                wager = 1
            else:
                if (user_balance < 3000):
                    wager = user_balance
                elif (user_balance < 10000):
                    wager = int(user_balance * .5)
                else:
                    wager = int(user_balance * 0.05)

            try:
                placebet(session, fighter, wager)
            except:
                print("Error placing bet.")

            prev_balance = user_balance
            placed_bet = True
            Salty_Bet.clear()
            Salty_Bet.update({'Balance':user_balance, 'P1':player1name, 'P2':player2name, 'P1-win':Pa, 'P2-win':Pb, 'Wager':wager, 'GameMode':game_mode})

        elif (prev_status == 'open' and status == 'locked'):
            if (int(site.get_player1_wagers()) > int(site.get_player2_wagers())):
                odds = int(site.get_player1_wagers()) / int(site.get_player2_wagers())
                if (fighter == player.P1):
                    odds = 1 / odds
            else:
                odds = int(site.get_player2_wagers()) / int(site.get_player1_wagers())
                if (fighter == player.P2):
                    odds = 1 / odds
            print_bet_details(current_bet, wager, odds)
            print_site_message(site.get_remaining())
            Salty_Bet.update({'Odds':odds})

        elif (prev_status != '1' and status == '1'):
            print_winner(site.get_player1_name())
            (Wr, Lr) = DetermineNewRankings(player1stats.get('elo'), Pb, player2stats.get('elo'), Pa)
            db.insert_ranking(site.get_player1_name(), Wr, site.get_player2_name(), Lr)
            Salty_Bet.update({'Winner':'P1'})

        elif (prev_status != '2' and status == '2'):
            print_winner(site.get_player2_name())
            (Wr, Lr) = DetermineNewRankings(player2stats.get('elo'), Pb, player1stats.get('elo'), Pa)
            db.insert_ranking(site.get_player2_name(), Wr, site.get_player1_name(), Lr)
            Salty_Bet.update({'Winner':'P2'})

if __name__ == '__main__':
    main()


