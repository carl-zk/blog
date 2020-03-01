#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import unquote
import json
import hashlib
import signal
import sys

s = requests.Session()

def signal_handler(sig, frame):
    s.close()
    print('\nYou pressed Ctrl+C!')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

username = 'carl-zk'
oauth_token = '9b2873f8f7a1329b213ad58fde78dbf8bf4dbd44'
repo_name = 'gitalk'
sitemap_url = "https://carl-zk.github.io/blog/sitemap.xml"
label = 'Gitalk'

headers = {
        'Authorization': f'token {oauth_token}',
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"}

api = f"https://api.github.com/repos/{username}/{repo_name}/issues"

r = s.get(sitemap_url).text

soup = BeautifulSoup(r, 'xml')
sitemapTags = soup.find_all("url")

total, number, inited = len(sitemapTags), 1, 0
for url in sitemapTags:
    print(f"{number}th of {total}, inited={inited}")
    number += 1
    title = re.search('\/blog/.*', url.findNext("loc").text)[0]
    ID = hashlib.md5(title.encode())
    r = s.get(api, params={'labels': [label, ID.hexdigest()]}, headers=headers)
    if len(r.json()) == 0 or len(r.json()[0]['url']) < 1:
        inited += 1
        print('init comments of: ' + unquote(title))
        r = s.post(api, json={'title':unquote(title), 'labels':[label, ID.hexdigest()]}, headers=headers)
        print(r.json())
    else:
        break
s.close()
print("ALL DONE!")
