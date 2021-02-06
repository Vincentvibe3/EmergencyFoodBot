
from .bot import createbot, startbot
from . import db

def setupbot():
    local = False
    beta = True
    print('Setting up databases...')
    db.setup(local=local, beta=beta)
    db.createnameroulette()
    db.createspotify()
    print('Creating bot instance...')
    bot, TOKEN = createbot(local=local, beta=beta)
    print('Starting bot...\n')
    startbot(bot, TOKEN)

setupbot()