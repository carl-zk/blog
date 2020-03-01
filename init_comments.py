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
oauth_token = '5d08e22e0c782e8d223b944f2ead604dd7a2a919'
repo_name = 'gitalk'
sitemap_url = "https://carl-zk.github.io/blog/sitemap.xml"
label = 'Gitalk'

headers = {
        'Authorization': f'token {oauth_token}',
        'User-Agent': 'Mozilla/5.0 Chrome/70.0'}

api = 'https://api.github.com/repos/' + username + '/' + repo_name + '/issues'

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
    if not r.json():
    	inited += 1
    	print('init comments of: ' + unquote(title))
    	r = s.post(api, json={'title':unquote(title), 'labels':[label, ID.hexdigest()]}, headers=headers)
s.close()
print("ALL DONE!")



