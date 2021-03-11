import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE weight
          (id INTEGER PRIMARY KEY ASC, 
           user_id INTEGER NOT NULL,
           user_name VARCHAR(250) NOT NULL,
           weight INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE calories
          (id INTEGER PRIMARY KEY ASC, 
           user_id INTEGER NOT NULL,
           user_name VARCHAR(250) NOT NULL,
           calories INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
