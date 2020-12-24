import discord
from discord.ext import commands
import random
import typing
import time
import os
import asyncio

#command modules
import Sauce as s
import Kana_Practice as kp
import spotify

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
async def sauce(ctx, *, tags: typing.Optional[str] = 'English'):
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
            randomsauce = s.randomsauce(ctx, tags)
            await randomsauce.send_sauce()   
    
        else: 
            await ctx.send('This command can only be used in NSFW channels')

@bot.command(aliases = ['rs'])
async def readsauce(ctx, id, *, i: typing.Optional[int]=1):
    if ctx.channel.is_nsfw():
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
                read = s.read(ctx, id, owner, i)
                await read.send_image()
                timeout = time.time()+10*60
                while time.time() < timeout:
                    await read.edit_message(timeout)
        
    else: 
        await ctx.send('This command can only be used in NSFW channels')

@bot.command(aliases = ['pk'])
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

@bot.command(aliases = ['sp'])
async def spotifyrecs(ctx, username=''):
    check = await spotify.check_membership(ctx)
    if check and username == '':
        recommendations = spotify.recommendations(ctx)
        await recommendations.get_recommendations()
    elif check and username != '':
        await ctx.send('The username only needs to be given on registration')
        recommendations = spotify.recommendations(ctx)
        await recommendations.get_recommendations()
    elif not check and username == '':
        await ctx.send('Please register first by giving your username')
    else:
        register = spotify.register(ctx, username)
        await register.register() 

#testing commands
@bot.command()
async def testsauce(ctx, testtimes:int, *, tags: typing.Optional[str] = 'English'):
    if ctx.author == bot.get_user(321812737812594688):
        for i in range(testtimes):
            print(i)
            await sauce(ctx, tags=tags)
        await purgebots(ctx, limit=testtimes)
    else:
        await ctx.send('You do not have the required permissions')

def is_bot(ctx):
    return ctx.author == bot.get_user(774017121243365384) or ctx.author == bot.get_user(772251680103464970) or ctx.author == bot.get_user(772256300389236767)

@bot.command()
async def purgebots(ctx, limit=None):
    if ctx.author == bot.get_user(bot.owner_id) or bot:
        await ctx.channel.purge(limit=limit, check=is_bot, bulk=True)
    else:
        await ctx.send('You do not have the required permissions')

bot.run(TOKEN)
