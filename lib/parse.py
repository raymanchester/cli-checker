from bs4 import BeautifulSoup
import requests
import threading
from queue import Queue
import time
from lib.proxy import *
from lib.log import *
from lib.replace import replace
from lib.configure import enableProxy as PROXY
from lib.proxy import *
from lib.configure import getSite as SITE
from lib.configure import numThreads as THREADS
from lib.configure import getWordList as WORD_LIST

s = requests.Session()
print_lock = threading.Lock()

# Reads word list from file and adds each name to array words[]
fx = open(WORD_LIST(), 'r')
words = fx.read().split('\n')
fx.close()

def parseJob(item):
    word = words[item]
    link = replace(word)
    if PROXY:
        pl = get_proxy_list()
        select_random_proxy(pl)
        if check_proxy():
            r = s.get(link, proxies=proxyDict)
        else:
            pl = get_proxy_list()
            select_random_proxy(pl)
            r = s.get(link, proxies=proxyDict)
    else:
        r = s.get(link)
    page = r.content
    soup = BeautifulSoup(page, "html.parser")
    matches = []
    if SITE() == 5:
        # Available
        match1 = soup.body.findAll(text='The specified profile could not be found.')
        # Taken
        match2 = soup.body.findAll(text='This profile is private.')
        match3 = soup.find('div', attrs={'class': 'profile_header'})
        
        matches = [match1, match2, match3]
    elif SITE() == 6:
        # Available
        match1 = soup.body.findAll(text='No group could be retrieved for the given URL.')
        # Taken
        match2 = soup.body.findAll(text='Request To Join')
        match3 = soup.find('div', attrs={'class': 'grouppage_header'})

        matches = [match1, match2, match3]
    else:
        print("Wrong site!")

    with print_lock:
        log_result(r, word, link, matches=matches)
            

def threader():
    while True:
        item = q.get()
        parseJob(item)
        q.task_done()

start = time.time()

q = Queue()
for x in range(THREADS()):
    t = threading.Thread(target = threader)
    t.daemon = True
    t.start()

for item in range(words.__len__()):
    q.put(item)

q.join()

total = str(time.time()-start)
print("\n\nEntire job took: %s seconds" % total)