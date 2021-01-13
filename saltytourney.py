import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import random

#local imports
import authenticate
from placebet import *
from consoledisplay import *
import saltysite
import config
import saltydb
from elo import *

def parse_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.find('table', id='bracket')

def parse_table(table):
    n_columns = 0
    n_rows = 0
    column_names = []

    for row in table.find_all('tr'):
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows += 1;
            if n_columns == 0:
                n_columns = len(td_tags)
        
        th_tags = row.find_all('th')
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())
        

    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0,n_columns)
    df = pd.DataFrame(columns = columns, index= range(0,n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1
    
    return df

def lookup_ELO(db, fighter):
    player = db.retrieve_fighter(fighter)
    return player.get('elo')

def determine_match_winners(fighters):
    winners = []
    sim_games = 9999
    for i in zip(fighters[0::2], fighters[1::2]):
        (Pa, Pb) = ExpectedProbabilities(i[0][1], i[1][1])
        play_game = random.randrange(0, sim_games, 1)
        if(play_game < (Pa * sim_games)):
            Pa = Pa * 100
            print(f'Fighter: {i[0][0]} | {Pa:.0f}%')
            winners.append(i[0])
        else:
            Pb = Pb * 100
            print(f'Fighter: {i[1][0]} | {Pb:.0f}%')
            winners.append(i[1])
    return winners

def main():

    db = saltydb.Database('saltybet.sqlite3.bin')

    table = parse_url(config.TOURNEY_URL)
    df = parse_table(table)

    fighters = df[df['Round 1'] != ""].loc[:,'Round 1'].values
    fighters = [(fighter,lookup_ELO(db, fighter)) for fighter in fighters]

    print('\nRound 1 Winners')
    first_rnd_winners = determine_match_winners(fighters)
    print('\nRound 2 Winners')
    second_rnd_winners = determine_match_winners(first_rnd_winners)
    print('\nRound 3 Winners')
    third_rnd_winners = determine_match_winners(second_rnd_winners)
    print('\nChampion')
    champion = determine_match_winners(third_rnd_winners)

    df_projected = df.copy()

    df_projected['Round 2'][1] = first_rnd_winners[0][0]
    df_projected['Round 2'][5] = first_rnd_winners[1][0]
    df_projected['Round 2'][9] = first_rnd_winners[2][0]
    df_projected['Round 2'][13] = first_rnd_winners[3][0]
    df_projected['Round 2'][17] = first_rnd_winners[4][0]
    df_projected['Round 2'][21] = first_rnd_winners[5][0]
    df_projected['Round 2'][25] = first_rnd_winners[6][0]
    df_projected['Round 2'][29] = first_rnd_winners[7][0]

    df_projected['Round 3'][3] = second_rnd_winners[0][0]
    df_projected['Round 3'][11] = second_rnd_winners[1][0]
    df_projected['Round 3'][19] = second_rnd_winners[2][0]
    df_projected['Round 3'][27] = second_rnd_winners[3][0]

    df_projected['Final'][7] = third_rnd_winners[0][0]
    df_projected['Final'][23] = third_rnd_winners[1][0]

    df_projected['Winner'][15] = champion[0][0]
    print('\nProjected Bracket:')
    print(df_projected)

    # logic for the table:
    # only one fighter per row
    # Round 1: 0, 2 | 4, 6  | 8, 10   |  12, 14
    # Round 2:   1  |   5   |   9     |   13
    # Round 3:       3      |        11
    # Final  :                  7
    # add 16 to each above to get lower part of bracket
    # Winner :                                    15

    # put all fighters in a list (0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30)
    # each entry becomes a tuple consisting of (fighter, ELO)
    # taken in order, each two becomes a fight
    # create a new list for round 2 winners
    # push to specific locations in the data frame
    # taken in order, each two becomes a fight
    # create a new list for round 3 winners
    # push to specific locations in the data frame
    # do the final and update






if __name__ == '__main__':
    main()

