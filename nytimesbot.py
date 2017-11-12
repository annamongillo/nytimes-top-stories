#!/usr/bin/python3

import time
import re
import requests
import json
import MySQLdb as mdb
from slackclient import SlackClient
import datetime

def message_matches(user_id, message_text):
    '''
    Check if the username and the word 'bot' appears in the text
    '''
    regex_expression = '.*@' + user_id + '.*bot.*'
    regex = re.compile(regex_expression)
    # Check if the message text matches the regex above
    match = regex.match(message_text)
    # returns true if the match is not None (ie the regex had a match)
    return match != None 

def extract_entity(message_text):
    regex_expression = "headlines containing (.+)"
    regex= re.compile(regex_expression)
    matches = regex.finditer(message_text)
    for match in matches:
        # return the first captured phrase
        # which is between "on" and "station"
        return match.group(1) 
    
    # if there were no matches, return None
    return None

def gettitles(entity): 
    con = mdb.connect(host = 'localhost', 
                  user = 'root',
                  database = 'nytimes',
                  passwd = 'dwdstudent2015', 
                  charset='utf8', use_unicode=True);

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT * FROM Headlines WHERE title LIKE %s ", ('%'+entity+'%',))
    headlines = list(cur.fetchall())
    matching_headlines=[headline['title']+ "//"+headline['published_date'].strftime('%m-%d-%Y') for headline in headlines]
    cur.close()
    return matching_headlines

def create_message(username, entity):
    if entity != None:
        # We want to address the user with the username. Potentially, we can also check
        # if the user has added a first and last name, and use these instead of the username
        message = "Thank you @{u} for asking about headlines containing ".format(u=username)+entity+". "
        matching_headlines = gettitles(entity)
        # If we cannot find any matching headline...
        if len(matching_headlines) == 0:
            message += " I could not find any matching headlines.\n"
        # If there are multiple matching headlines
        if len(matching_headlines) >= 1:
            message += 'See headlines here: http://ec2-52-0-84-157.compute-1.amazonaws.com:5000/search?title='+entity
    else:
        message =  "Thank you @{u} for asking NYTimesBot a question. ".format(u=username) 
        message+="Unfortunately I did not understand the keyword you are asking for. "
        message+="Ask me about `headlines containing xxxx` and I will try to answer."
    return message

secrets_file = 'slack_secret.json'
f = open(secrets_file, 'r') 
content = f.read()
f.close()

auth_info = json.loads(content)
auth_token = auth_info["access_token"]
bot_user_id = auth_info["user_id"]

sc = SlackClient(auth_token)
sc.rtm_connect()

if sc.rtm_connect():
    while True:
        time.sleep(1)
        response = sc.rtm_read()
        for item in response:
            if item.get("type") != 'message':
                continue
            if item.get("user") == None:
                continue
            message_text = item.get('text')
            if not message_matches(bot_user_id, message_text):
                continue  
            response = sc.api_call("users.info", user=item["user"])
            username = response['user'].get('name')
            entity = extract_entity(message_text)
            message = create_message(username, entity)
            sc.api_call("chat.postMessage", channel="#assignment2_bots", text=message)