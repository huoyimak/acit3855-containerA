import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE IF EXISTS weight
          ''')

c.execute('''
          DROP TABLE IF EXISTS calories
          ''')

conn.commit()
conn.close()