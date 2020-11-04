import discord
from discord.ext import commands
import time

async def checkReactions(ctx, tempMessage, currentnumber, max, owner, timeout):
    emojis = ['⏮️', '◀️', '▶️', '⏭️']
    for emoji in emojis:
        await tempMessage.add_reaction(emoji=emoji)

    message = await ctx.fetch_message(tempMessage.id)
    while True:
        messageReactions = message.reactions
        for r in messageReactions:
            if time.time() >= timeout:
                    return currentnumber
            elif ctx.author in await r.users().flatten() or owner in await r.users().flatten():
                if r == messageReactions[0]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    return 1
                if r == messageReactions[1]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    if currentnumber > 1:
                        return currentnumber-1
                    else: 
                        return currentnumber
                if r == messageReactions[2]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    if currentnumber < max:
                        return currentnumber+1
                    else:
                        return currentnumber
                if r == messageReactions[3]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    return max