import os
import wget
import sqlite3
import math

#constant K - we can tweak in here

def Probability(rating1, rating2):
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def DetermineNewRankings(winnerRa, winnerPa, loserRb, loserPb):
    winnerRa = winnerRa + K * (1 - winnerPa) 
    loserRb = loserRb + K * (0 - loserPb)
    return (winnerRa, loserRb)
    
def ExpectedProbabilities(Ra, Rb):
    Pa = Probability(Rb, Ra)    #Probability of Player A
    Pb = Probability(Ra, Rb)    #Probability of Player B
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

def download_file(local_path, link):
    if not os.path.exists(local_path):
        print("Downloading from %s, this may take a while..." % link)
        wget.download(link, local_path)
        print()
    return local_path


# add steps to go download latest sqlite database from github
# add ranking field

K = 30

# download the latest database from imaprettykitty
database = download_file("saltybet.sqlite3.bin", "https://salty.imaprettykitty.com/saltybet.sqlite3.bin")

# connect to the database
conn = db_connect("saltybet.sqlite3.bin")
cur = conn.cursor()

cur.execute('DROP TABLE current')
cur.execute('ALTER TABLE rankings ADD COLUMN elo default 1000')

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
