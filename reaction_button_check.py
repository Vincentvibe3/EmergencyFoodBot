import discord
from discord.ext import commands
bot = commands.Bot(command_prefix="$")

async def checkReactions(ctx, tempMessage, currentnumber, max, owner):
    emojis = ['⏮️', '◀️', '▶️', '⏭️']
    for emoji in emojis:
        await tempMessage.add_reaction(emoji=emoji)

    message = await ctx.fetch_message(tempMessage.id)
    while True:
        messageReactions = message.reactions
        for r in messageReactions:
            if ctx.author in await r.users().flatten() or owner in await r.users().flatten():
                if r == messageReactions[0]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    return 1
                if r == messageReactions[1]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    return currentnumber-1
                if r == messageReactions[2]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    return currentnumber+1
                if r == messageReactions[3]:
                    await r.remove(ctx.author)
                    await r.remove(owner)
                    return max