import discord
from discord.ext import commands
import random
import typing
import os
import asyncio

#command modules
import Sauce_finder as sf
import Sauce_reader as sr
import reaction_button_check as rbc

#import token
TOKEN = os.environ['TOKEN']
#command prefix
commandPrefix = '$'
bot = commands.Bot(command_prefix="$")
description = '''$'''

#ready message
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    await bot.change_presence(activity= discord.Game('Kevin is horny'))
    print('\nAdded in following servers:')
    for guilds in bot.guilds:
        print(" -"+str(guilds))

#commands
@bot.command()
async def say(ctx, *, arg):
    await ctx.send(arg)

@bot.command()
async def sauce(ctx, *, tags: typing.Optional[str] = ''):
    if ctx.channel.is_nsfw():
        sauceUrl = await sf.randomUrl(tags)
        await ctx.send(sauceUrl)    
    
    else: 
        await ctx.send('This command can only be used in NSFW channels')

@bot.command()
async def readsauce(ctx, number):
    if ctx.channel.is_nsfw():
        pagenumbers = int(await sr.pagenumbers(number))
        galleryUrl = await sr.galleryUrl(number)
        i = 1
        image = await sr.checkpage(galleryUrl, i)
        tempMessage = await ctx.send(image)
        while i <= pagenumbers:
            i = await rbc.checkReactions(ctx, tempMessage, i, pagenumbers)
            newImage = await sr.checkpage(galleryUrl, i)
            await tempMessage.edit(content=newImage)
    
    else: 
        await ctx.send('This command can only be used in NSFW channels')

bot.run(TOKEN)