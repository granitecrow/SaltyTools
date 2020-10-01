from bs4 import BeautifulSoup
import requests
import time
import json

#local imports
import config

class scrape:
    def __init__(self, session, request):
        # Match session
        self.session = session
        self.request = request
        self.match_json = json.loads(session.get(config.STATE_URL).content)

        # Match Details
        soup = BeautifulSoup(request.content, 'html.parser')
        self.balance = int(soup.find(id="balance").string.replace(',',''))
        self.betStreak = soup.find("span", id="betStreak")
        self.leaderboardRank = soup.find("span", id="leaderboardRank")

    def get_USER_bet_streak(self):
        return self.betStreak.text

    def get_USER_leaderboard_rank(self):
        return self.leaderboardRank.text

    def get_USER_balance(self):
        return self.balance

    def get_betting_status(self):
        return self.match_json['status']

    def get_json(self):
        return self.match_json

    def get_player1_name(self):
        return self.match_json['p1name']

    def get_player1_wagers(self):
        return str(self.match_json['p1total']).replace(',','')

    def get_player2_name(self):
        return self.match_json['p2name']

    def get_player2_wagers(self):
        return str(self.match_json['p2total']).replace(',','')

    def get_remaining(self):
        return self.match_json['remaining']

    def update(self):
        # Refresh the request
        self.request = self.session.get(self.request.url)

        # Check to see if the match status changed
        refreshContent = self.session.get(config.STATE_URL).content
        if refreshContent == None or refreshContent == "":
            print('None or empty for data file')
        else:
            new_match = json.loads(refreshContent)

        if (self.match_json != new_match):
            self.match_json = new_match
            soup = BeautifulSoup(self.request.content, 'html.parser')
            self.balance = int(soup.find(id="balance").string.replace(',',''))
            self.betStreak = soup.find("span", id="betStreak")
            self.leaderboardRank = soup.find("span", id="leaderboardRank")
