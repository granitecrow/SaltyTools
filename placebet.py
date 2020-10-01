import requests
import config

def placebet(session, player, amount):
    payload = {
        'radio':'on',
        'selectedplayer':player.value, 
        'wager':amount
        }
    r = session.post(config.BET_URL, data=payload)