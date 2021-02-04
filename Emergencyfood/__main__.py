
from .bot import createbot, startbot
from . import db

def setupbot():
    local = False
    print('Setting up databases...')
    db.setup(local=local)
    db.createnameroulette()
    db.createspotify()
    print('Creating bot instance...')
    bot, TOKEN = createbot(local=local)
    print('Starting bot...\n')
    startbot(bot, TOKEN)

setupbot()