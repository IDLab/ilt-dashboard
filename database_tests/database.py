import mysql.connector

try:
	cnx = mysql.connector.connect(
    user='s1946250', password='MAA.R.RM.R.S',
    host='mysql.liacs.leidenuniv.nl',
    database='s1946250')
except:
	print("Connection could not be established")
	exit()
