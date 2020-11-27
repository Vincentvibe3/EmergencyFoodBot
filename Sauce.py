import discord
from discord.ext import commands
import time
import random
import aiohttp
import asyncio
import json

async def search(query):
    """searches nhentai with the specified search query"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://nhentai.net/api/galleries/search?query=%s' %(query)) as searchResult:
            results = await searchResult.json()
            return results

async def checktag(sauce, tagsToCheck):
    """check that the hentai contains the specified tags"""
    sauceTags = sauce['tags']
    tagnames = []
    for tags in sauceTags:
        tagnames.append(tags['name'])

    for tag in tagsToCheck:
        if tag.lower() not in tagnames:
            return False
        else:
            continue
    
    return True

async def getsauce(id):
    """gets info for a specific hentai"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://nhentai.net/api/gallery/%s' %(id)) as result:
            sauce = await result.json()
            return sauce

class randomsauce():
    """sends random hentai to discord"""
    def __init__(self, ctx, tags):
        self.url = 'https://nhentai.net/g/'
        self.ctx = ctx
        if tags.lower() == 'all':
            self.random = True
        else:
            self.random = False
        self.tagslist = tags.split(', ')
    
    async def get_search_query(self):
        """formats the tags to form a search query"""
        tags=[]
        for tag in self.tagslist:
            elements = tag.split()
            for element in elements:
                tags.append(element)

        query = ''
        for word in tags:
            query = query + word + "+"
        return query[:-1]

    async def get_random_sauce(self):
        """gets a random hentai with specified tags"""
        query = await randomsauce.get_search_query(self)
        results = await search(query)
        if not results['result']:
            await self.ctx.send('There is no matching sauce')
        else:
            num_pages = results['num_pages']
            checkTags = False
            while not checkTags:
                randomPageNum = random.randint(1, num_pages)
                for tries in range(3):
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get('https://nhentai.net/api/galleries/search?query=%s&page=%s' %(query, randomPageNum)) as randomPage:
                                if randomPage.status == 429:
                                    raise Exception("Too Many Requests")
                    except Exception:
                        await asyncio.sleep(4)
                        continue
                    else:
                        break

                randomPageResult = await randomPage.json()
                randomSauce = random.choice(randomPageResult['result'])
                checkTags = await checktag(randomSauce, self.tagslist)
            return randomSauce['id']

    async def send_sauce(self):
        """send url to discord"""
        if self.random:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nhentai.net/random', allow_redirects=True) as site:
                    await self.ctx.send(site.url)
        else:
            sauceId = await randomsauce.get_random_sauce(self)
            await self.ctx.send(self.url+str(sauceId))

class read():
    """sends an embed with the url to a hentai page with controls to read"""
    def __init__(self, ctx, id, owner, currentpage):
        self.url = 'https://i.nhentai.net/galleries/'
        self.extensions = {'j':'.jpg', 'p':'.png', 'g':'.gif'}
        self.id = id
        self.ctx = ctx
        self.owner = owner
        self.currentpage = currentpage

    async def get_sauce_info(self):
        """Get information for the specified hentai"""
        self.sauce = await getsauce(self.id)
        self.num_pages = self.sauce['num_pages']
        self.gallery_id = self.sauce['media_id']

    async def get_extension(self):
        """get a page's file extension"""
        exttype = self.sauce['images']['pages'][self.currentpage-1]['t']
        self.extension = self.extensions[exttype]

    async def send_image(self):
        """send image to discord"""
        await read.get_sauce_info(self)
        await read.get_extension(self)
        if self.currentpage < 1 or self.num_pages < self.currentpage:
            await self.ctx.send('This page does not exist')
        else:
            self.embed = discord.Embed()
            self.embed.set_footer(text="Page " + str(self.currentpage) + "/" + str(self.num_pages))
            self.embed.set_image(url=self.url+self.gallery_id+'/'+str(self.currentpage)+self.extension)
            self.message = await self.ctx.send(embed=self.embed)
            self.currentpage = await read.checkReactions(self)

    async def edit_message(self, timeout):
        """edits the message and embed after using controls"""
        await read.get_extension(self)
        self.embed.set_footer(text="Page " + str(self.currentpage) + "/" + str(self.num_pages))
        self.embed.set_image(url=self.url+self.gallery_id+'/'+str(self.currentpage)+self.extension)
        await self.message.edit(embed=self.embed)
        self.currentpage = await read.checkReactions(self, timeout=timeout)


    async def checkReactions(self, timeout=None):
        """adds controls and checks for controls"""
        emojis = ['⏮️', '◀️', '▶️', '⏭️']
        for emoji in emojis:
            await self.message.add_reaction(emoji=emoji)

        self.message = await self.ctx.fetch_message(self.message.id)
        while True:
            if timeout and timeout < time.time():
                break
            else:
                messageReactions = self.message.reactions
                for reaction in messageReactions:
                    if self.ctx.author in await reaction.users().flatten() or self.owner in await reaction.users().flatten():
                        if reaction == messageReactions[0]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            return 1
                        
                        if reaction == messageReactions[1]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            if self.currentpage > 1:
                                return self.currentpage-1
                            else: 
                                return self.currentpage
                        
                        if reaction == messageReactions[2]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            if self.currentpage < self.num_pages:
                                return self.currentpage+1
                            else:
                                return self.currentpage
                        
                        if reaction == messageReactions[3]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            return self.num_pages

    

        
