#!/usr/bin/python3
# By Ttatanepvp123
# Github : https://github.com/ttatanepvp123
# License : GPL-3 ( https://www.gnu.org/licenses/gpl-3.0.en.html )
import re
import requests
import random
import _thread
import json
import time
import utils
import sys
import sqlite3

global links, linksChecked, threadUsed

with open("config.json") as fp:
    config = json.load(fp)

fileIsOpen = False
links = []
linksChecked = []
threadUsed = 0

def displayer():
    global links, linksChecked, threadUsed
    while True:
        print(f"links : {len(linksChecked)}/{len(links)+len(linksChecked)} | threads : {threadUsed}/{config['ThreadsMax']}   ", end="\r")
        time.sleep(0.5)

def checkLink():
    global links, linksChecked, threadUsed
    threadUsed += 1
    link = random.choice(links)
    links.remove(link)
    if not link in linksChecked:
        linksChecked.append(link)
        try:
            r = requests.get(link, headers=config["headers"], timeout=config["Timeout"])
            FoundedLinks = utils.getAllLinks(r)
            utils.saveUrl(r, config["StatusCode200Only"], config["fileName"], config["fileFormat"])
            for currentLink in FoundedLinks:
                if not currentLink in linksChecked:
                    links.append(currentLink)
        except Exception as e:
            if "--debug" in sys.argv:print(e)
    threadUsed -= 1

if not config["fileFormat"] in utils.supportedFormat: 
    print("format not supported :(")
    exit(2)
elif config["fileFormat"] == "SQLite":
    conn = sqlite3.connect(config["fileName"])
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS urls(
     id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     title TEXT,
     url TEXT,
     site TEXT,
     contentType TEXT,
     encoding TEXT,
     timestamp INTERGER
)
""")
    cursor.close()
    conn.commit()
    conn.close()

links.append(input("start link : "))

_thread.start_new_thread(displayer, ())

fakeDoWhile = False
while (len(links) != 0 and threadUsed != 0) or not fakeDoWhile:
    if threadUsed < config["ThreadsMax"] and len(links) != 0:
        _thread.start_new_thread(checkLink, ())
        time.sleep(0.05)
    elif len(links) == 0 and threadUsed == 0:
        fakeDoWhile = True