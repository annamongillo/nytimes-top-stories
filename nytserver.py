#!/bin/sh

from flask import Flask, render_template
import MySQLdb as mdb
from flask import request

app = Flask(__name__)

@app.route('/')
def nytimes_headlines():

    con = mdb.connect(host = 'localhost', 
                  user = 'root',
                  database = 'nytimes',
                  passwd = 'dwdstudent2015', 
                  charset='utf8', use_unicode=True);

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT title, published_date FROM Headlines")
    headlines = cur.fetchall()
    cur.close()
    con.close()

    return render_template('nytimes.html', headlines=headlines)

@app.route('/search')
def search():
    
    search = request.args.get('title')

    con = mdb.connect(host = 'localhost', 
                  user = 'root',
                  database = 'nytimes',
                  passwd = 'dwdstudent2015', 
                  charset='utf8', use_unicode=True);

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT * FROM Headlines WHERE title LIKE %s ", ('%'+search+'%',))
    headlines = cur.fetchall()
    cur.close()
    con.close()

    return render_template('nytimes.html', search=search, headlines=headlines)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)