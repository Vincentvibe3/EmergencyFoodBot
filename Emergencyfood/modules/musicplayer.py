import asyncio

import discord
import youtube_dl

YTDLOPTS={'default_search': 'ytsearch'}
ytdl = youtube_dl.YoutubeDL(YTDLOPTS)
FFMPEGOPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

config = {}

async def getstreaminfo(query):
    video = ytdl.extract_info(url=query, download=False)
    if "https://www.youtube.com/watch?v=" in query:
        formats = video["formats"]
        url = f'https://www.youtube.com/watch?v={video["id"]}'
        title = video['title']
    else:
        formats = video["entries"][0]["formats"]
        url = f'https://www.youtube.com/watch?v={video["entries"][0]["id"]}'
        title = video["entries"][0]['title']
    quality = []
    for fileformat in formats:
        if fileformat["acodec"] == "opus":
            quality.append((fileformat["abr"], fileformat["url"]))
    quality.sort()
    quality.reverse()
    
    return quality[0][1], title, url 

async def connect(ctx):
    voicechannel = ctx.message.author.voice.channel
    voiceclient = await voicechannel.connect()
    await ctx.guild.change_voice_state(channel=voicechannel, self_deaf=True)
    return voiceclient

async def add_to_queue(ctx, song):
    queue = config[str(ctx.guild.id)]['queue']
    stream, name, url = await getstreaminfo(song)
    queue.append((name, url, song))

async def playsong(ctx):
    voiceclient = await connect(ctx)
    queue = config[str(ctx.guild.id)]['queue']
    first = True
    while config[str(ctx.guild.id)]['loop'] or first==True:
        first = False
        for element in queue:
            stream, title, url = await getstreaminfo(element[2])
            audio =  discord.FFmpegPCMAudio(stream, **FFMPEGOPTS)
            voiceclient.play(audio)
            embed_color = discord.Colour.from_rgb(120, 205, 215)
            track_info = f'[{title}]({url})'
            embed = discord.Embed(title='Now Playing:', description=track_info, colour=embed_color)
            message = await ctx.send(embed=embed)
            while voiceclient.is_playing() and config[str(ctx.guild.id)]['skip'] is False:
                await asyncio.sleep(1)
            if config[str(ctx.guild.id)]['skip'] is True:
                config[str(ctx.guild.id)]['skip'] = False
                voiceclient.stop()
            await message.delete()
            

async def view_queue(ctx):
    queue = config[str(ctx.guild.id)]['queue']
    embed_color = discord.Colour.from_rgb(120, 205, 215)
    embed = discord.Embed(title='Queue:', colour=embed_color)
    for element in queue:
        embed.add_field(name=str(queue.index(element)+1), value=f'[{element[0]}]({element[1]})', inline=False)
    message = await ctx.send(embed=embed)

async def clear_queue(ctx):
    if str(ctx.guild.id) in config:
        del config[str(ctx.guild.id)]

async def resume(ctx):
    check = await checkpause(ctx)
    if check:
        ctx.voice_client.resume()
    else:
        await ctx.send("music must be paused to resume")

async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
    else:
        await ctx.send("the bot must be connected to stop")

async def disconnect(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("the bot must be connected to disconnect")

async def pause(ctx):
    check = await checkplay(ctx)
    if check:
        ctx.voice_client.pause()
    else:
        await ctx.send("You must be playing music to pause")

async def checkplay(ctx):
    if ctx.voice_client:
        return ctx.voice_client.is_playing()
    else:
        return False

async def checkpause(ctx):
    if ctx.voice_client:
        return ctx.voice_client.is_paused()
    else:
        return False

    