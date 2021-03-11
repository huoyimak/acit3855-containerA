import mysql.connector

db_conn = mysql.connector.connect(host="acit3855-kafka.eastus2.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE weight
          (id INT NOT NULL AUTO_INCREMENT, 
           user_id INTEGER NOT NULL,
           user_name VARCHAR(250) NOT NULL,
           weight INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT weight_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE calories
          (id INT NOT NULL AUTO_INCREMENT,
           user_id INTEGER NOT NULL,
           user_name VARCHAR(250) NOT NULL,
           calories INTEGER NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT calories_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
