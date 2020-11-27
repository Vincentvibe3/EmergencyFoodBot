import requests
import random
import aiohttp
import asyncio

def get_search_query(check):
        tags=[]
        for tag in check:
            elements = tag.split()
            for element in elements:
                tags.append(element)

        query = ''
        for word in tags:
            query = query+word+"+"
        query = query[:-1]
        return query

def gettagid():
    results = r.json()['result']
    for result in results:
        tags = result['tags']
        tagnames = {}
        toCheck = search.split(', ')
        for tag in tags:
            tagnames[tag['name']]=tag['id']
        for tag in toCheck:
            if tag not in tagnames:
                print('missing tag: ' + tag)
                return False
            else:
                continue
        
        all.append(result['id'])

# search = input('enter a tag\n')
# query = get_search_query(search.split(', '))
# all=[]
# r = requests.get('https://nhentai.net/api/galleries/search?query=%s' %(query))
# num_pages = r.json()['num_pages']
# for i in range(num_pages+1):
# #r = requests.get('https://nhentai.net/api/gallery/167738')
#     print(i)
#     gettagid()
#     r = requests.get('https://nhentai.net/api/galleries/search?query=%s&page=%s' %(query, i+1))
# print(all)
# print(len(all))   

r = requests.get('https://nhentai.net/api/galleries/tagged?tag_id=29433')
pages = r.json()['num_pages']
listsauce = []
for i in range(pages):
    page = requests.get('https://nhentai.net/api/galleries/tagged?tag_id=29433&page=%s' %(i+1))
    for result in page.json()['result']:
        tags = []
        for tag in result['tags']:
            tags.append(tag['name'])
        if 'english' in tags:
            listsauce.append(result['id'])
print(listsauce)
print(len(listsauce))
