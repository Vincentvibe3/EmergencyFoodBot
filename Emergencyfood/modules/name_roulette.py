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
        """The given user is a sql literal formed by psycopg2"""
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
        user = str(ctx.author.id)
        server_id = sql.Literal(str(ctx.guild.id))
        checkguild = await checkserver(server_id)
        if checkguild:
            check = await checkuser(user, server_id)
            if not check:
                userdict = await getUsers(server_id)      
                userdict[user] = {"name": ctx.author.name, "rolls":0, "deathroll":False}
                print(userdict)
                userjson = sql.Literal(json.dumps(userdict))
                query = sql.SQL("UPDATE servers SET users={users} WHERE id={server}").format(users=userjson, server=server_id,)
                cur.execute(query)
                
                await ctx.send('Registered')
            else:
                await ctx.send('You are already registered')
        else:
            await ctx.send('The server is not participating in a name roulette')

    @db.connect(database='nameroulette')
    async def unregisteruser(cur, ctx):
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
                await ctx.send('Unregistered')
            else:
                await ctx.send("You can't unregister if you are not registered")
        else:
            await ctx.send('The server is not participating in a name roulette')

    @db.connect(database='nameroulette')
    async def registerserver(cur, ctx):
        server_id = sql.Literal(str(ctx.guild.id))
        channel = sql.Literal(str(ctx.channel.id))
        check = await checkserver(server_id)
        if not check:
            query = sql.SQL("INSERT INTO servers (id, channel) VALUES({server_id}, {channel});").format(server_id=server_id, channel=channel)
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

    async def getroll(ctx, rollnum:int, choices:list):
        chances = [1, 2.5, 5]
        if not choices:
            await ctx.send('No possible rolls were found')
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
        return results[0]

    @db.connect(database='nameroulette')
    async def getDeathrolls(cur, server:sql.Literal):
        query = sql.SQL("SELECT deathrolls FROM servers WHERE id={server}").format(server=server)
        cur.execute(query)
        results = cur.fetchone()
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
            await ctx.send('server is not registered')

    async def reroll(ctx):
        user = str(ctx.author.id)
        server = sql.Literal(str(ctx.guild.id))
        users = await getUsers(server)
        userproperties = users[user]
        if userproperties['rolls'] < 3:
            message = await getmessage(ctx)
            newmessage = await updatemessage(message, ctx.author.name, 'hello')
            await message.edit(content=newmessage)
            userproperties['rolls'] += 1
            await updateusers(server, users)
        else:
            await ctx.send('You dont have any rolls left')

    @db.connect(database='nameroulette')
    async def updateusers(cur, server:sql.Literal, users:dict):
        usersjson = sql.Literal(json.dumps(users))
        query = sql.SQL("UPDATE servers SET users={users} WHERE id={server}").format(users=usersjson , server=server)
        cur.execute(query)

    async def updatemessage(message:discord.Message, username:str, newrole:str):
        newmessage = ''
        toParse = message.content.split('\n')
        for user in toParse[1:]:
            if username in user:
                toParse.append(f'{toParse[toParse.index(user)]}, {newrole}')
                del toParse[toParse.index(user)]
        for entry in toParse:
            newmessage = f'{newmessage}{entry}\n'
        return newmessage

    async def ping(ctx):
        server = sql.Literal(str(ctx.guild.id))
        deathroll = await setDeathRoll(server)
        choices = await getchoices(server)
        if deathroll == None:
            await ctx.send('No deathroles were set')
        elif choices == None:
            await ctx.send('No roles were set')
        else:
            pingrole = discord.utils.get(ctx.guild.roles, name='Name Roulette')
            await ctx.send(pingrole.mention)
            users = await getUsers(server)
            message = '***This weeks deathroll is {}***\n'.format(deathroll)
            for user in users:
                result = await getroll(ctx, 0, choices)
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

    async def start(ctx):
        while True:
            await registerserver(ctx)
            nexttime = await getNotifyTime(-5)
            now = time.time()
            waittime = nexttime-now
            await asyncio.sleep(waittime)
            await ping(ctx)