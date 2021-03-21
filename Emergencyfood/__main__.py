
if  __package__ == 'Emergencyfood':
    from .bot import createbot, startbot
    from . import db
    from .modules import spotify

    def setupbot():
        local = True
        beta = False
        print('Setting up databases...')
        db.setup(local=local, beta=beta)
        db.createnameroulette()
        db.createspotify()
        print('Setting up api secrets...')
        spotify.setupsecrets(local=local)
        print('Creating bot instance...')
        bot, TOKEN = createbot(local=local, beta=beta)
        print('Starting bot...\n')
        startbot(bot, TOKEN)

    setupbot()