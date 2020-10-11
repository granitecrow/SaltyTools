# TODO: create a user class that contains login credentials and stats
# TODO: log the result of the fight to the big database
# TODO: if we bet last round then update if we won or loss
# TODO: log the result of our betting to our database
# TODO: determine the wager for the fight
 
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
import saltysite
import config
import saltydb
from elo import *

class player(Enum):
    P1 = 'player1'
    P2 = 'player2'


def print_match_details(fighter1, fighter2, Pa, Pb):
    print("MATCH :: Fighter: {0} [ W: {1} | L: {2} | W%: {3} | R: {4:.0f}] Fighter: {5} [ W: {6} | L: {7} | W%: {8} | R: {9:.0f} ]".format(fighter1['fighter'], fighter1['wins'], fighter1['losses'], fighter1['win_ratio'], fighter1['elo'], fighter2['fighter'], fighter2['wins'], fighter2['losses'], fighter2['win_ratio'], fighter2['elo']))
    print("MATCH :: Fighter {0} has {1:.0%} probability of winning".format(fighter1['fighter'], Pa))
    print("MATCH :: Fighter {0} has {1:.0%} probability of winning".format(fighter2['fighter'], Pb))

def print_last_match_results(previous_balance, total_balance, placed_bet):
    if (previous_balance < total_balance):
        difference = total_balance - previous_balance
        print("WINNER :: ${}!".format(difference))
    elif (previous_balance > total_balance):
        difference = previous_balance - total_balance
        print("LOSER :: ${}!".format(difference))
    elif (placed_bet == False):
        print("- we did not place a bet-")
    else:
        print("Wait? Draws are possible? Or did you forget to bet? No change to balance.")

def print_welcome_message():
    print("WELCOME :: Let's GO!!!!!")

def print_user_stats(rank, streak, balance):
    print("USER STATS :: Rank: {0} | Bet Streak: {1} | Balance: {2}".format(rank, streak, balance))

def print_bet_details(fighter, wager, odds):
    potential_winning = wager * odds
    print("BET DETAILS :: Putting ${0} on {1} at {2:.2f} odds for a chance at ${3:.0f}".format(wager, fighter, odds, potential_winning))

def print_site_message(message):
    print("SALTY NOTE :: {}".format(message))

def print_winner(winner):
    print("WINNER: {} wins!".format(winner))

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
    duration = 0
    placed_bet = False

    while(True):
        time.sleep(7)

        prev_status = status
        site.update()
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

            print_last_match_results(prev_balance, user_balance, placed_bet)
            print_user_stats(site.get_USER_leaderboard_rank(), site.get_USER_bet_streak(), site.get_USER_balance())
            print_match_details(player1stats, player2stats, Pa, Pb)
            placed_bet = False

            # determine_fighter
            #if player1stats.get('win_ratio') > player2stats.get('win_ratio'):
            if Pa > Pb:
                fighter = player.P1
                current_bet = player1stats['fighter']
            else:
                fighter = player.P2
                current_bet = player2stats['fighter']

            # determine_wager
            if "bracket" in site.get_remaining():
                if (user_balance > 10000):
                    wager = int(user_balance * 0.1)
                else:
                    wager = user_balance
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

        elif (prev_status != '1' and status == '1'):
            print_winner(site.get_player1_name())
            (Wr, Lr) = DetermineNewRankings(player1stats.get('elo'), Pb, player2stats.get('elo'), Pa)
            db.insert_ranking(site.get_player1_name(), Wr, site.get_player2_name(), Lr)

        elif (prev_status != '2' and status == '2'):
            print_winner(site.get_player2_name())
            (Wr, Lr) = DetermineNewRankings(player2stats.get('elo'), Pb, player1stats.get('elo'), Pa)
            db.insert_ranking(site.get_player2_name(), Wr, site.get_player1_name(), Lr)

if __name__ == '__main__':
    main()


