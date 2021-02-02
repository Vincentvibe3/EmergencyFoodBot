from bot import createbot, startbot
import db

def setupbot():
    # db.createDB(local=False)
    bot, TOKEN = createbot(local=False)
    startbot(bot, TOKEN)

setupbot()