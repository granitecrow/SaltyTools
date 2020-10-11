import sqlite3



#page = requests.get("https://salty.imaprettykitty.com/search/?fighter=Yae")
#print(page.status_code)
#soup = BeautifulSoup(page.content, 'html.parser')
#print(list(soup.children))

#TABLES
#TABLE fights(id integer primary key autoincrement,winner text,loser text,count integer);
#TABLE rankings(id integer primary key autoincrement,fighter text,wins integer,losses integer,fights integer,win_ratio integer,lose_ratio integer);
#TABLE current(red text,blue text);
class Database(object):

    def __init__(self, db_name='saltybet.sqlite3.bin'):
        self.name = db_name
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.cursor.execute('create table if not exists rankings(id integer primary key autoincrement,fighter text,wins integer,losses integer,fights integer,win_ratio integer,lose_ratio integer)')
        self.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def connect(self):
        try:
            return sqlite3.connect(self.name)
        except sqlite3.Error as e:
            pass

    def commit(self):
        self.conn.commit()

    def ranking_from_query(self,query):
        return {'id':query[0],
            'fighter':query[1],
            'wins':query[2],
            'losses':query[3],
            'fights':query[4],
            'win_ratio':query[5],
            'lose_ratio':query[6],
            'elo':query[7]}

    def ranking_to_query(self,obj):
        return (obj['id'],
        obj['fighter'],
        obj['wins'],
        obj['losses'],
        obj['fights'],
        obj['win_ratio'],
        obj['lose_ratio'],
        obj['elo'])

    def retrieve_fighter(self, fighter):
        query_str='select * from rankings where fighter=?'
        self.cursor.execute(query_str,(fighter,))
        query = self.cursor.fetchone()
        if not query or len(query) != 8:
            query = (None, fighter, 0, 0, 0, 0, 0, 1000)
        ranking = self.ranking_from_query(query)
        return ranking

    def insert_ranking(self, winner, winner_rank, loser, loser_rank):
        # insert match to improve rankings
        insert_str='insert or replace into rankings(id,fighter,wins,losses,fights,win_ratio,lose_ratio,elo) values(?,?,?,?,?,?,?,?)'

        #Winner Entry
        winner=self.retrieve_fighter(winner)
        winner['wins']+=1
        winner['fights']+=1
        winner['win_ratio']=int(winner['wins']/float(winner['fights'])*100)
        winner['lose_ratio']=100-winner['win_ratio']
        winner['elo'] = winner_rank
        self.cursor.execute(insert_str,self.ranking_to_query(winner))
        self.commit()

        #Loser Entry
        loser=self.retrieve_fighter(loser)
        loser['losses']+=1
        loser['fights']+=1
        loser['win_ratio']=int(loser['wins']/float(loser['fights'])*100)
        loser['lose_ratio']=100-loser['win_ratio']
        loser['elo'] = loser_rank
        self.cursor.execute(insert_str,self.ranking_to_query(loser))
        self.commit()


    #def insert_fight(self, winner, loser):
        # insert fight results