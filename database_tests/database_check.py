import pandas as pd
import mysql.connector
import sys
import math
import os.path

# own import from database.py
from database import cnx

# check whether an argument is passed to the script
arguments = len(sys.argv) - 1

if arguments != 1:
    print ("Call file with \"python import_CSV_to_db.py nameofCSVfile\"")
    sys.exit()

# establish connection with the database
cursor = cnx.cursor()

# read input name from argument
inputName = sys.argv[1]

# create tablename
tableName = inputName.split(".")[0]

# check for existence input file exit if not found
if not os.path.isfile(inputName):
    print ("Inputfile: " + inputName + " not found!")
    sys.exit()
    
# read the data from the CSV file
df1 = pd.read_csv(inputName, encoding = "ISO-8859-1", dtype={'SBI': str})

rows = len(df1.index)
columns = len(df1.columns)
count = rows
nan_rows = []

# find the rows with nan values which will not be stored in the database
for i in range(rows):
    for j in range(1,columns):
        if (type(df1.iloc[i,j]) != str and math.isnan(df1.iloc[i,j])):
            count = count - 1
            nan_rows.append(i)
            break
            
# remove faulty entries            
for i in reversed(nan_rows):
    df1 = df1.drop(i)

# read the data from the database
query = "SELECT * FROM `" + tableName + "`;"
df2 = pd.read_sql(query, con=cnx)

# compare lengths
if count != len(df2.index):
    print ("Not all csv entries read.")
    sys.exit()
    
# compare values between database and csv file
for i in range(count):
    if (df1.iloc[i,1] != df2.iloc[i,1]):
        print ("Values in database do not match values in CSV.")
        print ("CSV value: ", end = '')
        print (df1.iloc[i,1])
        print ("Database value: ", end = '')
        print (df2.iloc[i,1])
        sys.exit()
    
print ("Values consistent")
