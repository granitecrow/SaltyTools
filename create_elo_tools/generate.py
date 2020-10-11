import os
import sqlite3
import math

# CREATE TABLE fights(id integer primary key autoincrement,winner text,loser text,count integer);
# add elo: ALTER TABLE ranking elo default 1000
# open database
# for each row of the fights table
# read elo rating of player 1
# read elo rating of player 2
#constant K - we can tweak in here

def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def DetermineNewRankings(winnerRa, winnerPa, loserRb, loserPb):
    winnerRa = winnerRa + K * (1 - winnerPa) 
    loserRb = loserRb + K * (0 - loserPb)
    return (winnerRa, loserRb)
    
def ExpectedProbabilities(Ra, Rb):
    #Probability of Player A
    Pa = Probability(Rb, Ra)
    #Probability of Player B
    Pb = Probability(Ra, Rb)
    return (Pa, Pb)

def db_connect(db_path):
    con = sqlite3.connect(db_path)
    return con

def get_fighter_rank(fighter):
    query_str = 'SELECT elo FROM rankings WHERE fighter=?'
    fightercur.execute(query_str,(fighter,))
    row = fightercur.fetchone()
    return row[0]

def set_fighter_rank(fighter, rank):
    query_str = 'UPDATE rankings SET elo=? WHERE fighter=?'
    fightercur.execute(query_str,(rank, fighter,))

database = "saltybet.sqlite3.bin"
K = 30

conn = db_connect(database)

cur = conn.cursor()
fightercur = conn.cursor()
query_str = 'UPDATE rankings SET elo=? WHERE fighter=?'

cur.execute('SELECT * FROM fights') 
for row in cur:
    (winner, loser) = row[1], row[2]

    try:
        Wr = get_fighter_rank(winner)
        Lr = get_fighter_rank(loser)
        print("{0} beat {1}".format(winner,loser))
        (Wp, Lp) = ExpectedProbabilities(Wr, Lr)
        (Wr, Lr) = DetermineNewRankings(Wr, Wp, Lr, Lp)

        set_fighter_rank(winner, Wr)
        set_fighter_rank(loser, Lr)

        conn.commit()
    except:
        pass

conn.close()
