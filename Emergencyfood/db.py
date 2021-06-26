
import os
import json

import psycopg2

DATABASES = {}
WORKSPACE_PATH = os.path.dirname(os.path.realpath(__file__))
SQL_PATH = os.path.join(WORKSPACE_PATH, 'SQL')

def setup(local=False, beta=False):
    global SSLMODE
    if local:
        projectpath = os.path.dirname(WORKSPACE_PATH)
        configfilepath = os.path.join(projectpath, 'localconfig.json')
        with open(configfilepath, 'r') as configfile:
            config = json.loads(configfile.read())
            DATABASES['spotify'] = config['spotify']['database']
            DATABASES['nameroulette'] = config['nameroulette']['database']
            SSLMODE = 'disable'
    elif beta:
        DATABASES['spotify'] = os.environ['HEROKU_POSTGRESQL_CHARCOAL_URL']
        DATABASES['nameroulette'] = os.environ['DATABASE_URL']
        SSLMODE = 'require'
    else:
        DATABASES['spotify'] = os.environ['HEROKU_POSTGRESQL_PURPLE_URL']
        DATABASES['nameroulette'] = os.environ['DATABASE_URL']
        SSLMODE = 'require'

def connect(database):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            conn = psycopg2.connect(DATABASES[database], sslmode=SSLMODE)
            with conn.cursor() as cur:
                result = await function(cur, *args, **kwargs)
                conn.commit()
            conn.close()
            return result
        return wrapper
    return decorator

def syncconnect(database):
    def decorator(function):
        def wrapper(*args, **kwargs):
            conn = psycopg2.connect(DATABASES[database], sslmode=SSLMODE)
            with conn.cursor() as cur:
                result = function(cur, *args, **kwargs)
                conn.commit()
            conn.close()
            return result
        return wrapper
    return decorator

@syncconnect(database='nameroulette')
def createnameroulette(cur):
    schemaPath = os.path.join(SQL_PATH, 'nameroulette.sql')
    with open(schemaPath) as schema:
        cur.execute(schema.read())
        
@syncconnect(database='nameroulette')
def createPing(cur):
    schemaPath = os.path.join(SQL_PATH, 'ping.sql')
    with open(schemaPath) as schema:
        cur.execute(schema.read())

@syncconnect(database='spotify')
def createspotify(cur):
    schemaPath = os.path.join(SQL_PATH, 'spotify.sql')
    with open(schemaPath) as schema:
        cur.execute(schema.read())
        

