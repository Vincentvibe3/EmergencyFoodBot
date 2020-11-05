import discord
from discord.ext import commands
import random
import typing
import time
import os
import asyncio

#command modules
import Sauce_finder as sf
import Sauce_reader as sr
import reaction_button_check as rbc
import Kana_Practice as kp

#import token
TOKEN = os.environ['TOKEN']
#command prefix
commandPrefix = '$'
bot = commands.Bot(command_prefix=commandPrefix)
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
    noRestriction = True
    if ctx.guild.name == "The Squad":
        authorRoles = []
        for role in ctx.author.roles:
            authorRoles.append(role.name)
        if 'Sauce for you' not in authorRoles:
            noRestriction = False
            await ctx.send('This role cannot use sauce commands')
        else:
            noRestriction = True
    if noRestriction == True:
        if ctx.channel.is_nsfw():
            sauceUrl = await sf.randomUrl(tags)
            await ctx.send(sauceUrl)    
    
        else: 
            await ctx.send('This command can only be used in NSFW channels')

@bot.command()
async def readsauce(ctx, number):
    noRestriction = True
    if ctx.guild.name == "The Squad":
        authorRoles = []
        for role in ctx.author.roles:
            authorRoles.append(role.name)
        if 'Sauce for you' not in authorRoles:
            noRestriction = False
            await ctx.send('This role cannot use sauce commands')
        else:
            noRestriction = True
    if noRestriction == True:
        if ctx.channel.is_nsfw():
            owner = bot.get_user(321812737812594688)
            pagenumbers = int(await sr.pagenumbers(number))
            galleryUrl = await sr.galleryUrl(number)
            i = 1
            image = await sr.checkpage(galleryUrl, i)
            tempMessage = await ctx.send(image)
            stoptime = time.time()+10*60
            while time.time() < stoptime:
                i = await rbc.checkReactions(ctx, tempMessage, i, pagenumbers, owner, stoptime)
                newImage = await sr.checkpage(galleryUrl, i)
                await tempMessage.edit(content=newImage)
        
        else: 
            await ctx.send('This command can only be used in NSFW channels')

@bot.command()
async def practicekana(ctx, mode=''):
    if mode.lower() in ['hiragana', 'katakana']:
        questionContent, answer = await kp.getQuestion(mode)
        await ctx.send(questionContent)
        try:
            timeout = time.time()+7
            while True:
                userAnswer = await bot.wait_for('message', timeout=timeout-time.time())
                if userAnswer.author == ctx.author:
                    break
                else:
                    continue
                
            if userAnswer.content == answer:
                await ctx.send('Your answer is correct')
            else:
                await ctx.send('The correct answer was ' + answer)

        except:
            await ctx.send('Too slow. The answer was "' + answer +'"')
    elif mode == '':    
        await ctx.send('You must specify a mode(hiragana or katakana)') 
    else:
        await ctx.send('Please enter a valid mode(hiragana or katakana)')


bot.run(TOKEN)
