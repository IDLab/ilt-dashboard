import os

import mysql.connector

# Try to read environment variables. Otherwise, replace by hand.
try:
	cnx = mysql.connector.connect(
    user=os.environ['DATABASEUSER'], 
    password=os.environ['DATABASEPASSWD'],
    host=os.environ['HOST'],
    database=os.environ['DATABASE'])
except:
	raise Exception("Connection could not be established")
