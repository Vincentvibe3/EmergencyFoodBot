from bot import createbot, startbot
import db

def setupbot():
    local = False
    # db.createDB(local=local)
    bot, TOKEN = createbot(local=local)
    startbot(bot, TOKEN)

setupbot()