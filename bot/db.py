import os

PATH = os.path.dirname(os.path.realpath(__file__))

def createDB(local=False):
    schemaPath = os.path.join(PATH, 'SQL/create_db.sql')
    with open(schemaPath) as schema:
        print(schema.read())