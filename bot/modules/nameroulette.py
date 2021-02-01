import time
import psycopg2
import random
import math
import os
import asyncio

from datetime import datetime, timedelta, timezone

DATABASE_URL = os.environ['DATABASE_URL']

async def openconnection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

async def getchoices():
    conn = await openconnection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM standardrolls')
        results = cur.fetchall()
    conn.close()
    return results


async def getNotifyTime(tz):
    timezonecorrect = timedelta(hours=tz)
    now = datetime.now(timezone.utc)
    weekday = now.weekday()
    daydifference = timedelta((12-weekday)%7)
    nextday = now+daydifference
    notify = nextday.replace(hour=20, minute=0, second=0)-timezonecorrect
    notifyepoch = notify.timestamp()
    return notifyepoch

async def roll():
    pass


async def ping(ctx):
    ctx.send('@nameroulette')

async def start(ctx):
    while True:
        nexttime = await getNotifyTime(-5)
        now = time.time()
        waittime = nexttime-now
        await asyncio.sleep(waittime)
        users = await getUsers(ctx)
        await setDeathRole()
        await ping(ctx, users)
        await clearuserstate()

async def getresults(ctx):
    get = await checkuserstate()
    if get:
        #connect database get deathrole

        #connect database get all rows

        # results= #database rows as list
        deathrolenum =  math.floor(len(results)/19) #5 percent of total
        for deathrole in range(deathrolenum):
            results.append('deathrole')
        
        result1 = random.choice(results)
        result2 = random.choice(results)
        result3 = random.choice(results)
        while result1 == result2:
            result2 = random.choice(results)
        while result2 == result3:
            result3 = random.choice(results)
        if result1 == 'deathrole' or result2 == 'deathrole':
            await ctx.send('You got the deathrole({})'.format(deathrole))
        else:
            await ctx.send('Your choices are {}, {} and {}'.format(result1, result2, result3))
        await checkselection()
        await writeuserstate(selection, result1, result2)
    else:
        await ctx.send('You have already gotten your results this week')

async def getUsers(ctx):
    participants = []
    for member in ctx.channel.members:
        for role in member.roles:
            if role.name == 'Name Roulette':
                participants.append(member)
            else:
                continue

async def setDeathRole():
    #connect database
    pass

async def setChoices(choices):
    #connect database
    pass

async def signup():
    #database
    pass

async def checkchoicesgiven():
    #databse
    pass

async def clearallchoices():
    #database
    pass

async def unregister():
    #database
    pass

async def checkselection():
    #reactions
    pass

async def clearuserstate():
    #database
    pass

async def writeuserstate():
    #database
    pass

async def checkuserstate():
    #database 
    pass