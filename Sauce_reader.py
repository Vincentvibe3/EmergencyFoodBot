import aiohttp
from html.parser import HTMLParser
import asyncio

class PARSEPAGE(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if str(tag) == "a":
            if ('class', 'last') in attrs:
                global currenttag 
                currenttag = HTMLParser.get_starttag_text(self)        

async def galleryUrl(number):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nhentai.net/g/%s/1/' %(number), allow_redirects=True) as site:
                    siteContent = await site.text()
                    start = siteContent.find('https://i.nhentai.net/galleries/')
                    end = siteContent.find('.jpg')
                    if end == -1:
                        end = siteContent.find('.png')
        return (siteContent[start:(end-1)])

async def pagenumbers(number):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nhentai.net/g/%s/1/' %(number), allow_redirects=True) as site:
                    siteContent = await site.text()
                    PARSEPAGE().feed(siteContent)
                    start = currenttag.find('/g/%s/'%(number))
                    end = currenttag.find('/"')
        return currenttag[start+len('/g/%s/'%(number)):end]

async def checkpage(url, i):
    async with aiohttp.ClientSession() as session:
        async with session.head(url+str(i)+'.jpg', allow_redirects=True) as site:
            if int(site.status) != 404:
                return str(url+str(i)+'.jpg')
            else:
                return str(url+str(i)+'.png')

