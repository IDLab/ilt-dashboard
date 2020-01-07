import mysql.connector

try:
	cnx = mysql.connector.connect(
    user='', password='',
    host='',
    database='')
except:
	print("Connection could not be established")
	exit()
