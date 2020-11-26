import requests
import random
import aiohttp
import asyncio

search = input('enter a tag\n')
#r = requests.get('https://nhentai.net/api/gallery/167738')
r = requests.get('https://nhentai.net/api/galleries/search?query=%s' %(search))
def gettagid():
    results = r.json()['result']
    for result in results:
        tags = result['tags']
        tagnames = {}
        toCheck = [search]
        for tag in tags:
            tagnames[tag['name']]=tag['id']
        for tag in toCheck:
            if tag not in tagnames:
                print('missing tag: ' + tag)
            else:
                return tagnames[tag]

tagid = gettagid()
r2 = requests.get("https://nhentai.net/api/galleries/tagged?tag_id=%s" %(tagid))
maxpage = r2.json()['num_pages']
randompage = random.randint(1, maxpage)
r3 = requests.get("https://nhentai.net/api/galleries/tagged?tag_id=%s&page=%s" %(tagid, randompage))
results = r3.json()['result']
sauce = random.choice(results)
print('https://nhentai.net/g/%s' %(sauce['id']))
print(sauce)
input()