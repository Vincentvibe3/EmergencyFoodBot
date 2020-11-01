import requests
import aiohttp
import asyncio

async def randomUrl(tags):
    tags = tags.split()
    isEnglish = -1
    if tags == []:
        while isEnglish == -1:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nhentai.net/random', allow_redirects=True) as site:
                    siteContent = await site.text()
                    isEnglish = siteContent.find('/language/english')
        return site.url
    
    else:
        tagsCheck = []
        while isEnglish == -1 or '0' in tagsCheck:
            tagsCheck =[]
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nhentai.net/random', allow_redirects=True) as site:
                    siteContent = await site.text()
                    isEnglish = siteContent.find('/language/english')
                    print(site.url)
            for tag in range(0, len(tags)):
                if siteContent.find(tags[tag]) == -1:
                    tagsCheck.append('0')
                    break
                else:
                    continue

        return site.url
