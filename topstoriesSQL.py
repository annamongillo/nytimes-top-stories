#!/usr/bin/python3

import requests
import json
import time
import MySQLdb as mdb
from datetime import datetime

# Get the data from the NYTimes Top Stories API
url = "https://api.nytimes.com/svc/topstories/v2/home.json?api-key=815512165c1244589cb0b6be02fb59f7"    

con = mdb.connect(host = 'localhost', 
                  user = 'root', 
                  passwd = 'dwdstudent2015', 
                  charset='utf8', use_unicode=True);

# Run a query to create a database that will hold the data
db_name = 'nytimes'
create_db_query = "CREATE DATABASE IF NOT EXISTS {db} DEFAULT CHARACTER SET 'utf8'".format(db=db_name)

# Create a database
cursor = con.cursor()
cursor.execute(create_db_query)
cursor.close()

cursor = con.cursor()
table_name = 'Headlines'
# Create a table for top headlines
create_table_query = '''CREATE TABLE IF NOT EXISTS {db}.{table} 
                                (title varchar(250), 
                                published_date datetime,
                                PRIMARY KEY(title)
                                )'''.format(db=db_name, table=table_name)
cursor.execute(create_table_query)
cursor.close()

# Fetch the data
results = requests.get(url).json() 
data = results["results"]

table_name = 'Headlines'
query_template = '''INSERT IGNORE INTO {db}.{table}(title, 
                                            published_date) 
                    VALUES (%s, %s)'''.format(db=db_name, table=table_name)
cursor = con.cursor()

for entry in data:
    title = entry['title']
    published_date = entry['published_date']               
    print("Inserting headline", title)
    query_parameters = (title, published_date)
    cursor.execute(query_template, query_parameters)

con.commit()
cursor.close()

cur = con.cursor(mdb.cursors.DictCursor)
cur.execute("SELECT * FROM {db}.{table}".format(db=db_name, table=table_name))
rows = cur.fetchall()
cur.close()
