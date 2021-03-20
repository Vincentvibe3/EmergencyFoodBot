import discord
import youtube_dl
ytdl = youtube_dl.YoutubeDL()
import json

async def play(ctx):
    url = 'https://r1---sn-t0a7sn7d.googlevideo.com/videoplayback?expire=1616290224&ei=UE1WYLOFMYXlhwaL_KuIBg&ip=192.0.226.2&id=o-ALkSnWRlO3pdYGKpNfyJ_lNYD0YlsAKZCOajgoTa375H&itag=249&source=youtube&requiressl=yes&mh=md&mm=31%2C26&mn=sn-t0a7sn7d%2Csn-tt1eln7e&ms=au%2Conr&mv=m&mvi=1&pl=21&initcwndbps=1308750&vprv=1&mime=audio%2Fwebm&ns=DDZD-J_tqxe2__55FaB4-rwF&gir=yes&clen=1604029&dur=254.401&lmt=1613290142666290&mt=1616268274&fvip=1&keepalive=yes&fexp=24001373%2C24007246&c=WEB&txp=5531432&n=Qfoefj3wwAlK2n2YXo&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIhAO9JA9qP_9qMlgz2T5EJjPzh7WTp77ajQ3dIxjZDOdJWAiAIrBan4r-sG58gBit36lKFFofy4roxlNLSIU5BUAnUog%3D%3D&sig=AOq0QJ8wRQIhAKGQ4S-8fQd2YWU7XFaizRCDQIjWjy7PzS-Nvd14pj3DAiBYZvBeYYinqtd6GceZgxTMi5_bPF-_YczJ1fkYtZXNiA=='
    voicechannel = ctx.message.author.voice.channel
    voiceclient = await voicechannel.connect()
    video = ytdl.extract_info(url='https://www.youtube.com/watch?v=ENcnYh79dUY', download=False)
    dumpfile = open("video.json", 'w')
    dumpfile.write(json.dumps(video, indent=4))
    audio =  discord.FFmpegPCMAudio(url)
    voiceclient.play(audio)
    