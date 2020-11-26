import discord
from discord.ext import commands
import time
import random
import aiohttp
import asyncio

async def search(query):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://nhentai.net/api/galleries/search?query=%s' %(query)) as searchResult:
            results = await searchResult.json()
            return results['result']

def checktag(sauce, tag):
    sauceTags = sauce['tags']
    tagnames = []
    for tags in sauceTags:
        tagnames.append(tags['name'])

    if tag not in tagnames:
        return False
    else:
        return True

async def getsauce(id):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://nhentai.net/api/gallery/%s' %(id)) as result:
            sauce = await result.json()
            return sauce

async def main():
    sauce = await getsauce('212121')
    print(sauce)

class read():
    def __init__(self, ctx, sauce, owner, currentpage):
        self.url = 'https://i.nhentai.net/galleries/'
        self.extensions = {'j':'.jpg', 'p':'.png', 'g':'.gif'}
        self.sauce = sauce
        self.ctx = ctx
        self.owner = owner
        self.currentpage = currentpage
        self.num_pages = self.sauce['num_pages']
        self.gallery_id = self.sauce['media_id']

    def get_extension(self):
        exttype = self.sauce['images']['pages'][self.currentpage-1]['t']
        self.extension = self.extensions[exttype]

    async def send_image(self):
        read.get_extension(self)
        if self.currentpage < 1 or self.num_pages < self.currentpage:
            await self.ctx.send('This page does not exist')
        else:
            self.embed = discord.Embed()
            self.embed.set_footer(text="Page " + str(self.currentpage) + "/" + str(self.num_pages))
            self.embed.set_image(url=self.url+self.gallery_id+'/'+str(self.currentpage)+self.extension)
            self.message = await self.ctx.send(embed=self.embed)

    async def edit_message(self):
        read.get_extension(self)
        self.embed.set_footer(text="Page " + str(self.currentpage) + "/" + str(self.num_pages))
        self.embed.set_image(url=self.url+self.gallery_id+'/'+str(self.currentpage)+self.extension)
        await self.message.edit(embed=self.embed)


    async def checkReactions(self):
        emojis = ['⏮️', '◀️', '▶️', '⏭️']
        for emoji in emojis:
            await self.message.add_reaction(emoji=emoji)

        self.message = await self.ctx.fetch_message(self.message.id)
        exit = True
        while exit:
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

    

        