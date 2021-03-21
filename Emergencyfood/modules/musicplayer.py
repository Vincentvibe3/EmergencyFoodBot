import asyncio

import discord
import youtube_dl

YTDLOPTS={'default_search': 'ytsearch'}
ytdl = youtube_dl.YoutubeDL(YTDLOPTS)
FFMPEGOPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

async def getstreaminfo(query):
    video = ytdl.extract_info(url=query, download=False)
    if "https://www.youtube.com/watch?v=" in query:
        formats = video["formats"]
    else:
        formats = video["entries"][0]["formats"]
    quality = []
    for fileformat in formats:
        if fileformat["acodec"] == "opus":
            quality.append((fileformat["abr"], fileformat["url"]))
    quality.sort()
    quality.reverse()
    url = f'https://www.youtube.com/watch?v={video["entries"][0]["id"]}'
    return quality[0][1], video["entries"][0]['title'], url 

async def connect(ctx):
    voicechannel = ctx.message.author.voice.channel
    voiceclient = await voicechannel.connect()
    await ctx.guild.change_voice_state(channel=voicechannel, self_deaf=True)
    return voiceclient

async def playsong(ctx, song):
    if ctx.voice_client:
        voiceclient = ctx.voice_client
    else:
        voiceclient = await connect(ctx)

    stream, title, url = await getstreaminfo(song)
    audio =  discord.FFmpegPCMAudio(stream, **FFMPEGOPTS)
    voiceclient.play(audio)
    embed_color = discord.Colour.from_rgb(120, 205, 215)
    track_info = f'[{title}]({url})'
    embed = discord.Embed(title='Playing:', description=track_info, colour=embed_color)
    await ctx.send(embed=embed)

async def resume(ctx):
    check = await checkpause(ctx)
    if check:
        ctx.voice_client.resume()
    else:
        await ctx.send("music must be paused to resume")

async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("the bot must be connected to stop")

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

    