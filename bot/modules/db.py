import os
import json
import psycopg2
import asyncio

DATABASES = {}
WORKSPACE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SQL_PATH = os.path.join(WORKSPACE_PATH, 'SQL')

def setup(local=False):
    if local:
        projectpath = os.path.dirname(WORKSPACE_PATH)
        configfilepath = os.path.join(projectpath, 'localconfig.json')
        with open(configfilepath, 'r') as configfile:
            config = json.loads(configfile.read())
            DATABASES['spotify'] = config['spotify']['database']
            DATABASES['nameroulette'] = config['nameroulette']['database']
    else:
        DATABASES['spotify'] = os.environ['HEROKU_POSTGRESQL_PURPLE_URL']
        DATABASES['nameroulette'] = os.environ['DATABASE_URL']

def connect(database):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            conn = psycopg2.connect(DATABASES[database])
            with conn.cursor() as cur:
                return await function(cur=cur, conn=conn, *args, **kwargs)
            conn.close()
        return wrapper
    return decorator

def syncconnect(database):
    def decorator(function):
        def wrapper(*args, **kwargs):
            conn = psycopg2.connect(DATABASES[database])
            with conn.cursor() as cur:
                return function(cur=cur, conn=conn, *args, **kwargs)
            conn.close()
        return wrapper
    return decorator

@syncconnect(database='nameroulette')
def createTABLES(cur, conn):
    schemaPath = os.path.join(SQL_PATH, 'create_db.sql')
    with open(schemaPath) as schema:
        cur.execute(schema.read())
        conn.commit()
