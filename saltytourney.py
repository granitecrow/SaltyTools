import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

#local imports
import authenticate
from placebet import *
from consoledisplay import *
import saltysite
import config
import saltydb
from elo import *

html_string = """
    <table id="bracket" style="margin: 0 auto;border-collapse:initial;">
            <tr><th>Round 1</th><th>Round 2</th><th>Round 3</th><th>Final</th><th>Winner</th></tr>
            <tr><td>Evil ryu sf3</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;Evil ryu sf3</td><td></td><td></td><td></td></tr>
            <tr><td>Turbo ken</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td>&nbsp;</td><td></td><td></td></tr>
            <tr><td>Evil ryu svc chaos</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;Evil ryu svc chaos</td><td></td><td></td><td></td></tr>
            <tr><td>E Ken</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td></td><td>&nbsp;</td><td></td></tr>
            <tr><td>Mahvel ryu</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;Mahvel ryu</td><td></td><td></td><td></td></tr>
            <tr><td>Evil ken</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td>&nbsp;</td><td></td><td></td></tr>
            <tr><td>Most evil ryu</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;Ken svc chaos</td><td></td><td></td><td></td></tr>
            <tr><td>Ken svc chaos</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td></td><td></td><td>&nbsp;</td></tr>
            <tr><td>Omega god ryu</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;Omega god ryu</td><td></td><td></td><td></td></tr>
            <tr><td>Mahvel ken</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td>&nbsp;</td><td></td><td></td></tr>
            <tr><td>Pocket evil ryu</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;Broken</td><td></td><td></td><td></td></tr>
            <tr><td>Broken</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td></td><td>&nbsp;</td><td></td></tr>
            <tr><td>Rainbow edition ryu</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;<span class="greentext">Pending</span></td><td></td><td></td><td></td></tr>
            <tr><td>Ssf2x ken</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td></td><td>&nbsp;</td><td></td><td></td></tr>
            <tr><td>Ryu EX3</td><td></td><td></td><td></td><td></td></tr>
            <tr><td></td><td>&nbsp;</td><td></td><td></td><td></td></tr>
            <tr><td>Ryu mvc1</td><td></td><td></td><td></td><td></td></tr>
        </table>
"""

def parse_url(url):
    response = requests.get(TOURNEY_URL)
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
    for i in zip(fighters[0::2], fighters[1::2]):
        (Pa, Pb) = ExpectedProbabilities(i[0][1], i[1][1])
        if (Pa > Pb):
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

    # test data; replace with parse_url function for live
    soup = BeautifulSoup(html_string, 'lxml')
    table = soup.find('table', id='bracket')
    df = parse_table(table)

    fighter_list = df['Round 1'].tolist()
    fighter_list = list(filter(lambda x: x != '', fighter_list))

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


    df['Round 2'][1] = first_rnd_winners[0][0]
    df['Round 2'][5] = first_rnd_winners[1][0]
    df['Round 2'][9] = first_rnd_winners[2][0]
    df['Round 2'][13] = first_rnd_winners[3][0]
    df['Round 2'][17] = first_rnd_winners[4][0]
    df['Round 2'][21] = first_rnd_winners[5][0]
    df['Round 2'][25] = first_rnd_winners[6][0]
    df['Round 2'][29] = first_rnd_winners[7][0]

    df['Round 3'][3] = second_rnd_winners[0][0]
    df['Round 3'][11] = second_rnd_winners[1][0]
    df['Round 3'][19] = second_rnd_winners[2][0]
    df['Round 3'][27] = second_rnd_winners[3][0]

    df['Final'][7] = third_rnd_winners[0][0]
    df['Final'][23] = third_rnd_winners[1][0]

    df['Winner'][15] = champion[0][0]
    print('\nBracket:')
    print(df)

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

