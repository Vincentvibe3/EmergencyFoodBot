import discord
from discord.ext import commands

async def checkReactions(ctx, tempMessage, currentnumber, max):
    emojis = ['⏮️', '◀️', '▶️', '⏭️']
    for emoji in emojis:
        await tempMessage.add_reaction(emoji=emoji)

    message = await ctx.fetch_message(tempMessage.id)
    while True:
        messageReactions = message.reactions
        for r in messageReactions:
            if ctx.author in await r.users().flatten():
                if r == messageReactions[0]:
                    await r.remove(ctx.author)
                    return 1
                if r == messageReactions[1]:
                    await r.remove(ctx.author)
                    return currentnumber-1
                if r == messageReactions[2]:
                    await r.remove(ctx.author)
                    return currentnumber+1
                if r == messageReactions[3]:
                    await r.remove(ctx.author)
                    return max