# Author : Ttatanepvp123
# Github : https://github.com/ttatanepvp123
# License : GPL-3 ( https://www.gnu.org/licenses/gpl-3.0.en.html )
import requests
from bs4 import BeautifulSoup
import re
import sys
import time
import sqlite3

global regexLinks, fileIsOpen, red, white, green

if not "--no-color" in sys.argv or "-nc" in sys.argv:
    red = "\033[0;31m"
    white = "\033[0m"
    green = "\033[0;32m"
else:
    red = ""
    white = ""
    green = ""

fileIsOpen = False
regexLinks = r"(http[s]://[a-zA-Z0-9\/\?=%\._\-]+)"

def getRealLink(link, url):
    if re.match(r"http[s]://", link) != None:
        return link
    elif link[0] == "/":
        return "/".join(url.split("/")[0:3])+link
    else:
        return "/".join(url.split("/")[0:len(url.split("/"))-1])+"/"+link

def getAllLinks(req : requests.Response):
    if "text/html" in req.headers["Content-Type"]:
        links = []
        soup = BeautifulSoup(req.text, "html.parser")
        for link in soup.find_all(["a", "link"]):
            tmp = link.get("href")
            if tmp != None:
                links.append(getRealLink(tmp, req.url))
        for link in soup.find_all(["img", "source", "script", "iframe"]):
            tmp = link.get("src")
            if tmp != None:
                links.append(getRealLink(tmp, req.url))
        for link in soup.find_all("form"):
            tmp = link.get("action")
            if tmp != None:
                links.append(getRealLink(tmp, req.url))
        return list(set(links))
    elif "text/" in req.headers["Content-Type"]:
        global regexLinks
        links = []
        for currentLink in re.findall(regexLinks, req.text):
            links.append(currentLink)
        return list(set(links))
    else:
        return []

supportedFormat = [
    "text",
    "SQLite"
]

def saveUrl(req, StatusCode200Only, fileName, format):
    global fileIsOpen, red, white, green
    edited = False
    if format == "text":
        while not edited:
            if not fileIsOpen:
                fileIsOpen = True
                tmp = False
                if req.status_code == 200:
                    print(f"{green}[ {white}200 {green}] {white} : {req.url}")
                    tmp = True
                else:
                    print(f"{red}[ {white}{req.status_code} {red}] {white} : {req.url}")
                    if not StatusCode200Only:
                        tmp = True
                if tmp:
                    with open("links.txt", "a+") as fp:
                        fp.write(req.url+"\n")
                fileIsOpen = False
                edited = True
            else:
                time.sleep(0.5)
    elif format == "SQLite":
        while not edited:
            if not fileIsOpen:
                fileIsOpen = True
                if req.status_code == 200:
                    print(f"{green}[ {white}200 {green}] {white} : {req.url}")
                    title = None
                    if "text/html" in req.headers["Content-Type"]:
                        try:
                            soup = BeautifulSoup(req.text, "html.parser")
                            title = soup.head.find('title').text
                        except:
                            pass
                    conn = sqlite3.connect(fileName)
                    cursor = conn.cursor()
                    data = {
                        "url":req.url,
                        "site":req.url.split("/")[2],
                        "encoding":str(req.encoding).upper(),
                        "timestamp":int(time.time()),
                        "contentType":req.headers["Content-Type"].split(";")[0],
                        "title":title
                    }
                    cursor.execute("INSERT INTO urls(title, url, site, encoding, timestamp, contentType) VALUES(:title, :url, :site, :encoding, :timestamp, :contentType)", data)
                    cursor.close()
                    conn.commit()
                    conn.close()
                else:
                    print(f"{red}[ {white}{req.status_code} {red}] {white} : {req.url}")
                fileIsOpen = False
                edited = True
            else:
                time.sleep(0.5)