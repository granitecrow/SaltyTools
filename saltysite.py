import requests
import time
import json
from bs4 import BeautifulSoup

#local imports
import config

class scrape:
    def __init__(self, session, request):
        """
        Parameters
        ----------
        session : Session
            session object that persists website parameters and cookies
        request : Response
            response object from server information
        """
        #TODO raise appropriate connection errors
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
        """Returns the current bet streak of the logged in user."""
        return self.betStreak.text

    def get_USER_leaderboard_rank(self):
        """Returns the current leaderboard ranking of the logged in user."""
        return self.leaderboardRank.text

    def get_USER_balance(self):
        """Returns the current balance ranking of the logged in user."""
        return self.balance

    def get_match_type(self):
        """Returns the current match type that is currently being running (Matchmaking, Tournament, Exhibition)."""
        note = self.match_json['remaining']
        if "left in the bracket" in note:               # '_ characters are left in the bracket!' -> tournament
            return "tournament"
        elif "exhibitions after the tournament" in note: # 'FINAL ROUND! Stay tuned for exhibitions after the tournament!' --> tournament
            return "tournament"
        elif "until the next tournament" in note:       # '_ more matches until the next tournament!' -> matchmaking
            return "matchmaking"
        elif "exhibition matches left" in note:         # '_ exhibition matches left!' --> exhibition
            return "exhibition"
        elif "Exhibition mode start" in note:           # 'Exhibition mode start!' --> exhibition
            return "exhibition"
        elif "after the next exhibition match" in note:  #'Matchmaking mode will be activated after the next exhibition match!'
            return "exhibition"
        else:
            return "exhibition" # because its safer to bet little!
      
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


    def get_retry(self):
        retries = 5
        while retries:
            try:
                return self.session.get(self.request.url)
            except:
                time.sleep(2)
                retries -= 1
        return self.get_retry()

    def update(self):
        """Returns the current state of the website by refreshing the session."""
        # Refresh the request
        self.request = self.get_retry()
        refreshContent = self.session.get(config.STATE_URL).content
        if(refreshContent != None or refreshContent != ''):
            try:
                new_match = json.loads(refreshContent)
            except ValueError:
                print('Response content is not valid JSON')
                pass

        if (self.match_json != new_match):
            try:
                self.match_json = new_match
                soup = BeautifulSoup(self.request.content, 'html.parser')
                self.balance = int(soup.find(id="balance").string.replace(',',''))
                self.betStreak = soup.find("span", id="betStreak")
                self.leaderboardRank = soup.find("span", id="leaderboardRank")
            except:
                pass