import mysql.connector
import sys

# own import from database.py
from database import cnx

# check whether an argument is passed to the script
arguments = len(sys.argv) - 1

if arguments != 1:
    print ("Call file with \"python droptable.py nameoftable\"")
    sys.exit()

# establish connection with the database
cursor = cnx.cursor()

# read input name from argument
tableName = sys.argv[1]

cursor.execute("DROP TABLE IF EXISTS `" + tableName + "`;")
