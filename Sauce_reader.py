import aiohttp
from html.parser import HTMLParser

class HTMLParser1(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if str(tag) == "a":
            if ('class', 'last') in attrs:
                global currenttag 
                currenttag = HTMLParser.get_starttag_text(self)        

async def galleryUrl(number):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nhentai.net/g/%s/1/' %(number), allow_redirects=True) as site:
                    siteContent = await site.text()
                    start = siteContent.find('/galleries/')
                    end = siteContent.find('.jpg')
        return ('https://i.nhentai.net'+siteContent[start:(end-1)])

async def pagenumbers(number):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://nhentai.net/g/%s/1/' %(number), allow_redirects=True) as site:
                    siteContent = await site.text()
                    HTMLParser1().feed(siteContent)
                    start = currenttag.find('/g/%s/'%(number))
                    end = currenttag.find('/"')
        return currenttag[9+len('/g/%s/'%(number)):end]
    
    # else:
    #     return 'stop being horny and just use a random sauce *bonk*'
    #     tagsCheck = []
    #     while isEnglish == -1 or '0' in tagsCheck:
    #         tagsCheck =[]
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get('https://nhentai.net/random', allow_redirects=True) as site:
    #                 siteContent = await site.text()
    #                 isEnglish = siteContent.find('/language/english')
    #                 print(site.url)
    #         for tag in range(0, len(tags)):
    #             if siteContent.find(tags[tag]) == -1:
    #                 tagsCheck.append('0')
    #                 break
    #             else:
    #                 continue

    #     return site.url
