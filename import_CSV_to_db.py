# Just run `python import_CSV_to_db.py [CSVfilename.csv]' and this script will import `CSVfilename.csv' into the database


import mysql.connector
from getpass import getpass
import pandas as pd
import json
import math
import sys
import os.path

# own import from database.py
from database import cnx

mysql_types = {
	"int": "INT",
	"float": "FLOAT",
	"string": "VARCHAR(300)",
	"shortstring": "VARCHAR(50)"
}


# check whether an argument is passed to the script
arguments = len(sys.argv) - 1

if arguments != 1:
    print ("Call file with \"python import_CSV_to_db.py nameofCSVfile\"")
    sys.exit()


# establish connection with the database
cursor = cnx.cursor()

# read input name from argument
inputName = sys.argv[1]

# check for existence input file exit if not found
if not os.path.isfile(inputName):
    print ("Inputfile: " + inputName + " not found!")
    sys.exit()

# generate name of config file
tableName = inputName.split(".")[0]
configName = tableName + ".specification.json"


# read configfile exit if not found
try:
    with open(configName, 'r') as confFile:
        data=confFile.read()
except IOError:
    print ("Configfile: " + configName + " not found!")
    sys.exit()

spec = json.loads(data)

# read the data from the CSV file
df = pd.read_csv(inputName, encoding = "ISO-8859-1", dtype={'SBI': str})



createStmt = "CREATE TABLE `" + tableName + "` ("
# for col in df.columns: 
# 	createStmt += "`" + col + "`" + " VARCHAR(100), "
for i in spec["columns"]:
	createStmt += "`" + i["name"] + "`" + " " + mysql_types[i["column"][1]] + ", "

# Add indexes:
for i in spec["indexes"]:
	if i["type"] == "primary":
		createStmt += "PRIMARY KEY ("
	elif i["type"] == "normal":
		createStmt += "INDEX ("
	else:
		continue
	# TODO coord index type

	for c in i["columns"]:
		createStmt += c + ", "
	createStmt = createStmt[0:-2]
	createStmt += "), "

createStmt = createStmt[0:-2]
createStmt += ");"

cursor.execute("DROP TABLE IF EXISTS `" + tableName + "`;")
cursor.execute(createStmt)

for index, row in df.iterrows():
	insertStmt = "INSERT INTO `" + tableName + "` ("

	# place all column names in insert statement, with a ',' as delimiter
	for i in spec["columns"]:
		insertStmt += i["name"] + ", "

	insertStmt = insertStmt[0: -2]
	insertStmt += ") VALUES ("

	broken = 0
	# insert the values
	for i in spec["columns"]:
		
		if(i["column"][1] == "string" or i["column"][1] == "shortstring"):
			insertStmt += "\"" + str(row[i["column"][0]]) + "\", "

		else:
			# check if the value is valid
			if(not math.isnan(row[i["column"][0]])):
				insertStmt += str(row[i["column"][0]]) + ", "

			else:
				broken = 1
				break

	if(broken == 1):
		continue

	insertStmt = insertStmt[0: -2]
	insertStmt += ");"
	cursor.execute(insertStmt)

cnx.commit()

cnx.close()
