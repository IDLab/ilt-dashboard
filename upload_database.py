"""
This program will import the csv file into the database (see database.py).

Please provide first credentials for the server in database.py (or in the 
environment variables as mentioned in that file.)
"""

import argparse
import json
import math
import os
import sys

import mysql.connector
import pandas as pd

# Read arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('csv_file', help="CSV file to read in.")
parser.add_argument(
	'specification_file', help="Specification file to read in."
)
args = parser.parse_args()

# own import from database.py
from connect_database import cnx

mysql_types = {
	"int": "INT",
	"float": "FLOAT",
	"string": "VARCHAR(300)",
	"shortstring": "VARCHAR(50)"
}

# establish connection with the database
cursor = cnx.cursor()

# read input name from argument
inputName = args.csv_file

# check for existence input file exit if not found
if not os.path.isfile(inputName):
    print ("Inputfile: " + inputName + " not found!")
    sys.exit()

# generate name of table
tableName = inputName.split("/")[-1].split(".")[0]

# read configfile exit if not found
try:
    with open(args.specification_file) as confFile:
        data=confFile.read()
except IOError:
    print ("Configfile: " + args.specification_file + " not found!")
    sys.exit()

spec = json.loads(data)

# read the data from the CSV file
df = pd.read_csv(inputName, encoding = "ISO-8859-1", dtype={'SBI': str})

# Create statement
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

for _, row in df.iterrows():
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
