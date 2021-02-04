import time
import random
import math
import asyncio
from datetime import datetime, timedelta, timezone
from psycopg2 import sql

from Emergencyfood import db

@db.connect(database='nameroulette')
async def getchoices(conn, cur):
    cur.execute('SELECT * FROM standardrolls')
    results = cur.fetchall()
    return results

@db.connect(database='nameroulette')
async def getDeathrolls(conn, cur):
    cur.execute('SELECT * FROM deathrolls')
    results = cur.fetchall()
    return results

async def setDeathRole():
    deathrolls = await getDeathrolls()
    deathroll = random.choice(deathrolls)[0]
    return deathroll

async def getNotifyTime(tz):
    timezonecorrect = timedelta(hours=tz)
    now = datetime.now(timezone.utc)
    weekday = now.weekday()
    daydifference = timedelta((12-weekday)%7)
    nextday = now+daydifference
    notify = nextday.replace(hour=20, minute=0, second=0)-timezonecorrect
    notifyepoch = notify.timestamp()
    return notifyepoch

@db.connect(database='nameroulette')
async def getrollcount(conn, cur, user):
    """The given user is a sql literal formed by psycopg2"""
    query = sql.SQL("SELECT rolls FROM users WHERE id={user_id}").format(user_id = user,)
    cur.execute(query)
    rollcount = cur.fetchone()
    return rollcount[0]

@db.connect(database='nameroulette')
async def writeuserstate(conn, cur, user, roll):
    user_id = sql.Literal(user)
    rollcount = await getrollcount(user_id)
    rolls = sql.Literal(rollcount+1)
    if roll == 'Death roll':
        death = True
    else:
        death = False
    deathroll = sql.Literal(death)
    query = sql.SQL("UPDATE users SET rolls={rolls}, deathroll={deathroll} WHERE id={id}").format(id=user_id, rolls=rolls, deathroll=deathroll,)
    cur.execute(query)
    conn.commit()

@db.connect(database='nameroulette')
async def registeruser(conn, cur, user):
    user_id = sql.Literal(user)
    query = sql.SQL("INSERT INTO users VALUES({id}, 0)").format(id=user_id,)
    cur.execute(query)
    conn.commit()

@db.connect(database='nameroulette')
async def checkserver(conn, cur, server_id):
    query = sql.SQL("SELECT EXISTS(SELECT 1 FROM servers WHERE id={server_id});").format(server_id=server_id)
    cur.execute(query)
    result = cur.fetchone()
    return result[0]

@db.connect(database='nameroulette')
async def registerserver(conn, cur, ctx):
    server_id = sql.Literal(str(ctx.guild.id))
    check = await checkserver(server_id)
    if not check:
        query = sql.SQL("INSERT INTO servers VALUES({server_id});").format(server_id=server_id)
        cur.execute(query)
        conn.commit()

async def roll(rollnum):
    choices = await getchoices()
    allrolls = []
    chances = [0.01, 0.025, 0.05]
    for choice in choices:
        allrolls.append(choice[0])
    for deathroll in range(math.floor(len(choices)*chances[rollnum])):
        allrolls.append('Death roll')
    result = random.choice(allrolls)
    return result

async def ping(ctx, users):
    ctx.send('@nameroulette')
    initialrolls = ''
    for user in users:
        result = await roll(0)
        initialrolls = f'{initialrolls}{user[0]}:{result}\n'
        await writeuserstate(user[0], roll)

@db.connect(database='nameroulette')
async def getUsers(ctx):
    cur.execute('SELECT * FROM users')
    participants = cur.fetchall()
    return participants

async def start(ctx):
    while True:
        await registerserver(ctx)
        nexttime = await getNotifyTime(-5)
        now = time.time()
        waittime = nexttime-now
        await asyncio.sleep(waittime)
        users = await getUsers(ctx)
        deathroll = await setDeathRole()
        await ping(ctx, users)
        await clearuserstate()
