from Emergencyfood.db import connect
import time
import random
import asyncio
import json
from datetime import datetime, timedelta, timezone

from psycopg2 import sql
import discord

if __package__ == 'Emergencyfood.modules':
    from Emergencyfood import db
    
    @db.connect(database='nameroulette')
    async def getrollcount(cur, user:sql.Literal):
        query = sql.SQL("SELECT rolls FROM users WHERE id={user_id}").format(user_id = user,)
        cur.execute(query)
        rollcount = cur.fetchone()
        return rollcount[0]

    @db.connect(database='nameroulette')
    async def checkserver(cur, server_id:sql.Literal):
        query = sql.SQL("SELECT EXISTS(SELECT 1 FROM servers WHERE id={server_id});").format(server_id=server_id)
        cur.execute(query)
        result = cur.fetchone()
        return result[0]

    async def checkuser(user:str, server:sql.Literal):
        result = await getUsers(server)
        if not result:
            return False
        else:
            if user not in result:
                return False
        return True      

    @db.connect(database='nameroulette')
    async def registeruser(cur, ctx):
        role = discord.utils.get(ctx.guild.roles, name='Name Roulette')
        await ctx.author.add_roles(role)
        user = str(ctx.author.id)
        server_id = sql.Literal(str(ctx.guild.id))
        checkguild = await checkserver(server_id)
        if checkguild:
            check = await checkuser(user, server_id)
            if not check:
                userdict = await getUsers(server_id)      
                userdict[user] = {"name": ctx.author.name, "rolls":0, "deathroll":False, "add": 3, "adddeath": 2}
                userjson = sql.Literal(json.dumps(userdict))
                query = sql.SQL("UPDATE servers SET users={users} WHERE id={server}").format(users=userjson, server=server_id,)
                cur.execute(query)
                
                message = 'Registered'
            else:
                message = 'You are already registered'
        else:
            message = 'The server is not participating in a name roulette'

        resp = await ctx.send(message)
        await resp.delete(delay=3)

    @db.connect(database='nameroulette')
    async def unregisteruser(cur, ctx):
        role = discord.utils.get(ctx.guild.roles, name='Name Roulette')
        await ctx.author.remove_roles(role)
        user = str(ctx.author.id)
        server_id = sql.Literal(str(ctx.guild.id))
        checkguild = await checkserver(server_id)
        if checkguild:
            check = await checkuser(user, server_id)
            if check and checkguild:
                userdict = await getUsers(server_id)
                del userdict[user]
                userjson = sql.Literal(json.dumps(userdict))
                query = sql.SQL("UPDATE servers SET users={users} WHERE id={server}").format(users=userjson, server=server_id,)
                cur.execute(query)
                message = 'Unregistered'
            else:
                message = "You can't unregister if you are not registered"
        else:
            message = 'The server is not participating in a name roulette'
        
        resp = await ctx.send(message)
        await resp.delete(delay=3)

    @db.connect(database='nameroulette')
    async def registerserver(cur, ctx):
        server_id = sql.Literal(str(ctx.guild.id))
        channel = sql.Literal(str(ctx.channel.id))
        check = await checkserver(server_id)
        if not check:
            query = sql.SQL("INSERT INTO servers (id, channel) VALUES({server_id}, {channel});").format(server_id=server_id, channel=channel)
        else:
            query = sql.SQL("UPDATE servers SET channel={channel} WHERE id={server_id};").format(server_id=server_id, channel=channel)
        cur.execute(query)

    @db.connect(database='nameroulette')
    async def getUsers(cur, server_id:sql.Literal):
        query = sql.SQL("SELECT users FROM servers WHERE id={server}").format(server=server_id)
        cur.execute(query)
        users = cur.fetchone()
        if users[0] is None:
                participants = {}
        else:
            participants = users[0]
        
        return participants

    async def getroll(rollnum:int, choices:list):
        chances = [1, 2.5, 5]
        if not choices:
            return None
        else:
            death = random.randint(0, 99)
            if death >= chances[rollnum]:
                result = random.choice(choices)
            else:
                result = 'Deathroll'
            return result

    @db.connect(database='nameroulette')
    async def getchoices(cur, server:sql.Literal):
        query = sql.SQL("SELECT standardrolls FROM servers WHERE id={server}").format(server=server)
        cur.execute(query)
        results = cur.fetchone()
        if results[0] == None:
            results = []
            return results
        return results[0]

    @db.connect(database='nameroulette')
    async def getDeathrolls(cur, server:sql.Literal):
        query = sql.SQL("SELECT deathrolls FROM servers WHERE id={server}").format(server=server)
        cur.execute(query)
        results = cur.fetchone()
        if results[0] == None:
            results = []
            return results
        return results[0]

    async def setDeathRoll(server:sql.Literal):
        deathrolls = await getDeathrolls(server)
        if not deathrolls:
            deathroll = None
        else:
            deathroll = random.choice(deathrolls)
        return deathroll

    @db.connect(database='nameroulette')
    async def writemessage(cur, message:str):
        formattedmess = sql.Literal(message)
        query = sql.SQL("UPDATE servers SET message={message}").format(message=formattedmess)
        cur.execute(query)

    @db.connect(database='nameroulette')
    async def getmessage(cur, ctx):
        server = sql.Literal(str(ctx.guild.id))
        check = await checkserver(server)
        if check:
            query = sql.SQL("SELECT message, channel FROM servers WHERE id={server}").format(server=server)
            cur.execute(query)
            result = cur.fetchone()
            channel = ctx.guild.get_channel(int(result[1]))
            partmessage = channel.get_partial_message(message_id=result[0])
            message = await partmessage.fetch()
            return message
        else:
            resp = await ctx.send('server is not registered')
            await resp.delete(delay=3)

    async def reroll(ctx):
        user = str(ctx.author.id)
        server = sql.Literal(str(ctx.guild.id))
        users = await getUsers(server)
        if user not in users:
            resp = await ctx.send('You can\'t reroll if you are not registered, register and wait for next week')
            await resp.delete(delay=3)
            return False
        userproperties = users[user]
        ok = False
        if userproperties['deathroll']:
            response = 'You cannot reroll because of the deathroll'
        elif userproperties['rolls'] < 3:
            choices = await getchoices(server)
            roll = await getroll(userproperties['rolls'], choices)
            message = await getmessage(ctx)
            newmessage = await updatemessage(ctx.author.name, user, message, roll, users)
            await message.edit(content=newmessage)
            userproperties['rolls'] += 1
            if roll == 'Deathroll':
                userproperties['deathroll'] = True
            await updateusers(server, users)
            ok = True
        else:
            response = 'You dont have any rolls left'
        
        if not ok:
            resp_mess = await ctx.send(response)
            await resp_mess.delete(delay=3)
        await updatenames(ctx)

    @db.connect(database='nameroulette')
    async def updateusers(cur, server:sql.Literal, users:dict):
        usersjson = sql.Literal(json.dumps(users))
        query = sql.SQL("UPDATE servers SET users={users} WHERE id={server}").format(users=usersjson , server=server)
        cur.execute(query)

    async def updatemessage(username:str, user_id:str, message:discord.Message, newrole:str, users:dict):
        old_username = users[user_id]['name']
        newmessage = ''
        toParse = message.content.split('\n')
        for user in toParse[1:]:
            if old_username in user:
                if newrole == 'Deathroll':
                    toParse.append(f'{username}: {newrole}')
                else:
                    user_entry = toParse[toParse.index(user)].split(':')
                    toParse.append(f'{username}:{user_entry[1]}, {newrole}')
                del toParse[toParse.index(user)]
        for entry in toParse:
            newmessage = f'{newmessage}{entry}\n'
        return newmessage

    async def ping(ctx):
        server = sql.Literal(str(ctx.guild.id))
        deathroll = await setDeathRoll(server)
        choices = await getchoices(server)
        if deathroll == None:
            await ctx.send('No deathrolls were set')
        elif choices == None:
            await ctx.send('No rolls were set')
        else:
            pingrole = discord.utils.get(ctx.guild.roles, name='Name Roulette')
            await ctx.send('------------\n'+pingrole.mention)
            users = await getUsers(server)
            message = '***This weeks deathroll is {}***\n'.format(deathroll)
            for user in users:
                result = await getroll(0, choices)
                message = f"{message}{users[user]['name']}: {result}\n"
                users[user]['rolls'] += 1
                if result == 'Deathroll':
                    users[user]['deathroll'] = True
            
            await updateusers(server, users)
            initialmessage = await ctx.send(message)
            await writemessage(str(initialmessage.id))

    async def getNotifyTime(tz:int):
        timezonecorrect = timedelta(hours=tz)
        now = datetime.now(timezone.utc)
        weekday = now.weekday()
        daydifference = timedelta((12-weekday)%7)
        nextday = now+daydifference
        notify = nextday.replace(hour=20, minute=0, second=0)-timezonecorrect
        notifyepoch = notify.timestamp()
        return notifyepoch

    @db.connect(database='nameroulette')
    async def registerChoices(cur, choices, ctx):
        server = sql.Literal(str(ctx.guild.id))
        user = str(ctx.author.id)
        users = await getUsers(server)
        addleft = users[user]['add']
        allchoices = await getchoices(server)
        redundant = []
        addcount = 0
        if addleft > 0:
            for choice in choices[:addleft]:
                if choice not in allchoices:
                    addcount+=1
                    allchoices.append(choice)
                else:
                    redundant.append(choice)
            
            if redundant:
                message = ''
                for entry in redundant:
                    message = f'{message}, {entry}'
                resp = await ctx.send(f'{message[1:]} was/were already in the rolls')
                await resp.delete(delay=3)

            users[user]['add'] = addleft-addcount
            await updateusers(server, users)

            jsonchoices = sql.Literal(json.dumps(allchoices))
            query = sql.SQL("UPDATE servers SET standardrolls={choices} WHERE id={server}").format(choices=jsonchoices, server=server)
            cur.execute(query)
        else:
            resp = await ctx.send('You do not have any entries left')
            await resp.delete(delay=3)

    @db.connect(database='nameroulette')
    async def registerDeathroll(cur, choices, ctx):
        server = sql.Literal(str(ctx.guild.id))
        user = str(ctx.author.id)
        users = await getUsers(server)
        addleft = users[user]['adddeath']
        allchoices = await getDeathrolls(server)
        redundant = []
        addcount = 0
        if addleft > 0:
            for choice in choices[:addleft]:
                if choice not in allchoices:
                    addcount+=1
                    allchoices.append(choice)
                else:
                    redundant.append(choice)
            
            if redundant:
                message = ''
                for entry in redundant:
                    message = f'{message}, {entry}'
                resp = await ctx.send(f'{message[1:]} was/were already in the deathrolls')
                await resp.delete(delay=3)
                
            users[user]['adddeath'] = addleft-addcount
            await updateusers(server, users)

            jsonchoices = sql.Literal(json.dumps(allchoices))
            query = sql.SQL("UPDATE servers SET deathrolls={choices} WHERE id={server}").format(choices=jsonchoices, server=server)
            cur.execute(query)
        else:
            resp = await ctx.send('You do not have any entries left')
            await resp.delete(delay=3)

    @db.connect(database='nameroulette')
    async def reset(cur, ctx):
        server = sql.Literal(str(ctx.guild.id))
        users = await getUsers(server)
        for user in users:
            users[user]['rolls'] = 0
            users[user]['deathroll'] = False
        await updateusers(server, users)

    @db.connect(database='nameroulette')
    async def updatenames(cur, ctx):
        server = sql.Literal(str(ctx.guild.id))
        users = await getUsers(server)
        for user_id in users:
            user = ctx.guild.get_member(int(user_id))
            users[user_id]['name'] = user.name
        await updateusers(server, users)

    async def listall(ctx):
        server = sql.Literal(str(ctx.guild.id))
        deathrolls = await getDeathrolls(server)
        standardrolls = await getchoices(server)
        message = await ctx.send(f'Death: {" ".join(deathrolls)}\nNormal: {" ".join(standardrolls)}')
        await message.delete(delay=3)

    @db.connect(database='nameroulette')
    async def updatedeath(cur, server:sql.Literal, rolls:list):
        rollsjson = sql.Literal(json.dumps(rolls))
        query = sql.SQL("UPDATE servers SET deathrolls={rolls} WHERE id={server};").format(rolls=rollsjson, server=server)
        cur.execute(query)

    @db.connect(database='nameroulette')
    async def updatechoices(cur, server:sql.Literal, rolls:list):
        rollsjson = sql.Literal(json.dumps(rolls))
        query = sql.SQL("UPDATE servers SET standardrolls={rolls} WHERE id={server};").format(rolls=rollsjson, server=server)
        cur.execute(query)

    async def remove(ctx, rolltype, choice):
        server = sql.Literal(str(ctx.guild.id))
        if rolltype == 'normal':
            choices = await getchoices(server)
            index = choices.index(choice)
            del choices[index]
            await updatechoices(server, choices)
            message = await ctx.send('removed')
        elif rolltype == 'death':
            deathrolls = await getchoices(server)
            index = deathrolls.index(choice)
            del deathrolls[index]
            await updatedeath(server, deathrolls)
            message = await ctx.send('removed')
        else:
            message = await ctx.send('An error occured: non-compliant type received')
        await message.delete(delay=3)

    async def start(ctx):
        while True:
            await registerserver(ctx)
            nexttime = await getNotifyTime(-5)
            now = time.time()
            waittime = nexttime-now
            await asyncio.sleep(waittime)
            await updatenames(ctx)
            await reset(ctx)
            await ping(ctx)
