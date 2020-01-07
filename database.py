import os

import mysql.connector

# Try to read environment variables. Otherwise, replace by hand.
try:
	cnx = mysql.connector.connect(
    user=os.environ['DBUSER'], 
    password=os.environ['DBPASS'],
    host=os.environ['HOST'],
    database=os.environ['DB'])
except:
	raise Exception("Connection could not be established")
