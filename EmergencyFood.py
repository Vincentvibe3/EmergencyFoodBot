import discord
import random
import requests
#import discordbot_commands
tokenSource = open('.token.txt', 'r') 
client = discord.Client()
TOKEN = tokenSource.read()
commandPrefix = '$'
description = '''$'''

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity= discord.Game("Kevin is horny"))

@client.event
async def on_message(message):
    commandName = 'say'
    if message.author == client.user:
        return

    if message.content.startswith(str(commandPrefix+commandName)):
        userMessage = message.content[len(commandPrefix+commandName):]
        await message.channel.send(userMessage)

@client.event
async def on_message(message):
    commandName = 'spam'
    if message.author == client.user:
        return

    if message.content.startswith(str(commandPrefix+commandName)):
        while True:
            userMessage = message.content[len(commandPrefix+commandName):]
            await message.channel.send(userMessage)

@client.event 
async def on_message(message):
    commandName = 'sauce'
    if message.author == client.user:
        return

    if message.content.startswith(str(commandPrefix+commandName)):
        if message.channel.is_nsfw():
            isEnglish = -1
            while isEnglish == -1:
                randomSauce = requests.head('https://nhentai.net/random', allow_redirects=True)
                siteContent = requests.get(randomSauce.url, allow_redirects=True).text
                isEnglish = siteContent.find('/language/english')
            await message.channel.send(randomSauce.url)
        else: 
            await message.channel.send("This command can only be used in NSFW channels")

client.run(TOKEN)