import discord
from discord.ext import commands
import time
import random
import aiohttp

async def search(query):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://nhentai.net/api/galleries/search?query=%s' %(query)) as searchResult:
            results = await searchResult.json()
            return results

async def checktag(sauce, tags):
     sauceTags = sauce['tags']
     tagnames = []
     for tags in sauceTags:
         tagnames.append(tags['name'])
    
     for tag in tags:
        if tag not in tagnames:
            return False
        else:
            continue
    
     return True

async def getsauce(id):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://nhentai.net/api/gallery/%s' %(id)) as result:
            sauce = await result.json()
            return sauce

class randomsauce():
    def __init__(self, ctx, tags):
        self.url = 'https://nhentai.net/g/'
        self.ctx = ctx
        if tags.lower() == 'all':
            self.random = True
        else:
            self.random = False
        self.tagslist = tags.split(',')
    
    async def get_search_query(self):
        tags=[]
        for tag in self.tagslist:
            elements = tag.split()
            for element in elements:
                tags.append(element)

        query = ''
        for word in tags:
            query = query+word+"+"
            self.query = query[:-1]

    async def get_random_sauce(self):
        await randomsauce.get_search_query(self)
        results = await search(self.query)
        if not results['result']:
            await self.ctx.send('There is no matching sauce')
        else:
            num_pages = results['num_pages']
            checkTags = False
            while not checkTags:
                randomPageNum = random.randint(0, num_pages)
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://nhentai.net/api/galleries/search?query=%s&Page=%s' %(self.query, randomPageNum)) as randomPage:
                        randomPageResult = await randomPage.json()
                        num_sauce = len(randomPageResult['result'])-1
                        randomSauce = random.randint(0, num_sauce)
                        await checktag(randomPageResult['result'], self.tagslist)
            self.sauceId = randomPageResult['result'][randomSauce]['id']

    async def send_sauce(self):
        if self.random:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://nhentai.net/random', allow_redirects=True) as site:
                    await self.ctx.send(site.url)
        else:
            await randomsauce.get_random_sauce(self)
            await self.ctx.send(self.url+str(self.sauceId))

class read():
    def __init__(self, ctx, id, owner, currentpage):
        self.url = 'https://i.nhentai.net/galleries/'
        self.extensions = {'j':'.jpg', 'p':'.png', 'g':'.gif'}
        self.id = id
        self.ctx = ctx
        self.owner = owner
        self.currentpage = currentpage

    async def get_sauce_info(self):
        self.sauce = await getsauce(self.id)
        self.num_pages = self.sauce['num_pages']
        self.gallery_id = self.sauce['media_id']

    async def get_extension(self):
        exttype = self.sauce['images']['pages'][self.currentpage-1]['t']
        self.extension = self.extensions[exttype]

    async def send_image(self):
        await read.get_sauce_info(self)
        await read.get_extension(self)
        if self.currentpage < 1 or self.num_pages < self.currentpage:
            await self.ctx.send('This page does not exist')
        else:
            self.embed = discord.Embed()
            self.embed.set_footer(text="Page " + str(self.currentpage) + "/" + str(self.num_pages))
            self.embed.set_image(url=self.url+self.gallery_id+'/'+str(self.currentpage)+self.extension)
            self.message = await self.ctx.send(embed=self.embed)
            await read.checkReactions(self)

    async def edit_message(self, timeout):
        await read.get_extension(self)
        self.embed.set_footer(text="Page " + str(self.currentpage) + "/" + str(self.num_pages))
        self.embed.set_image(url=self.url+self.gallery_id+'/'+str(self.currentpage)+self.extension)
        await self.message.edit(embed=self.embed)
        await read.checkReactions(self, timeout=timeout)


    async def checkReactions(self, timeout=None):
        emojis = ['⏮️', '◀️', '▶️', '⏭️']
        for emoji in emojis:
            await self.message.add_reaction(emoji=emoji)

        self.message = await self.ctx.fetch_message(self.message.id)
        exit = True
        while exit:
            if timeout and timeout > time.time():
                break
            else:
                messageReactions = self.message.reactions
                for reaction in messageReactions:
                    if self.ctx.author in await reaction.users().flatten() or self.owner in await reaction.users().flatten():
                        if reaction == messageReactions[0]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            self.currentpage =  1
                        
                        if reaction == messageReactions[1]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            if self.currentpage > 1:
                                self.currentpage =  self.currentpage-1
                            else: 
                                self.currentpage =  self.currentpage
                        
                        if reaction == messageReactions[2]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            if self.currentpage < self.num_pages:
                                self.currentpage =  self.currentpage+1
                            else:
                                self.currentpage = self.currentpage
                        
                        if reaction == messageReactions[3]:
                            await reaction.remove(self.ctx.author)
                            await reaction.remove(self.owner)
                            self.currentpage = self.num_pages
                        
                        exit = False

    

        
