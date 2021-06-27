import random
import asyncio
from psycopg2 import sql
from Emergencyfood import db, bot as mainBot

messages = ["""Greetings {mention},
We were informed of your activities. 
Please do not indulge in gaming. 
Look outside, your future will be brighter. :sunny: 
A message from the government of {guildName}""", """Hello, {mention}
https://youtu.be/zHL9GP_B30E
Goodbye.
-Michael Stevens""", """Hello {mention}. Stop playing games or your summer will be lost. This message was generated automatically."""]

pingAgain = True

@db.connect(database='nameroulette')
async def pingOsu(cur, bot):
    global pingAgain
    query = sql.SQL("SELECT * FROM ping;")
    cur.execute(query)
    result = cur.fetchone()
    channel = bot.get_channel(int(result[1]))
    sendChannel = bot.get_channel(int(result[2]))
    partmessage = channel.get_partial_message(message_id=result[0])
    message = await partmessage.fetch()
    ctx = await bot.get_context(message=message)
    mentions = ctx.message.mentions
    for member in mentions:
        activityNames = []
        for activity in member.activities:
            activityNames.append(activity.name)
        if 'osu!' in activityNames:
            if pingAgain:
                messageChoice = random.choice(message)
                await sendChannel.send(messageChoice.format(mention=member.mention, guildName=sendChannel.guild.name))
            pingAgain = False
        else:
            pingAgain = True

async def checkLoop(bot):
    while mainBot.running_ping_osu:
        await pingOsu(bot)
        await asyncio.sleep(30)

@db.connect(database='nameroulette')
async def registerPing(cur, ctx):
    delete = sql.SQL("DELETE FROM ping;")
    cur.execute(delete)
    channels = ctx.message.channel_mentions
    sendChannel = sql.Literal(channels[0].id)
    message = sql.Literal(ctx.message.id)
    channel = sql.Literal(ctx.channel.id)
    query = sql.SQL("INSERT INTO ping(message, channel, sendchannel) VALUES({message}, {channel}, {sendChannel});").format(message=message, channel=channel, sendChannel=sendChannel)
    cur.execute(query)
