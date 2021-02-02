import asyncio

from bot import createbot, startbot
from modules import db

def setupbot():
    local = True
    print('Setting up databases...')
    db.setup(local=local)
    db.createTABLES()
    print('starting bot...')
    bot, TOKEN = createbot(local=local)
    startbot(bot, TOKEN)

setupbot()