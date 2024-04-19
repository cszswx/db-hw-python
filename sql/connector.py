import pymysql
import os
from pathlib import Path
import json

CONFIG = json.load(open(Path(__file__).parent/'DB_CONFIG.json'))
SQL_ROOT_FOLDER = Path(__file__).parent

def get_db_connection():

    connection = pymysql.connect(host=CONFIG['DB_HOST'],
                                user=CONFIG['DB_USER'],
                                password=CONFIG['DB_PASSWORD'],
                                database=CONFIG['DB_DB'],
                                charset="utf8mb4",
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

def get_db_connection_multi():

    connection = pymysql.connect(host=CONFIG['DB_HOST'],
                                user=CONFIG['DB_USER'],
                                password=CONFIG['DB_PASSWORD'],
                                database=CONFIG['DB_DB'],
                                charset="utf8mb4",
                                cursorclass=pymysql.cursors.DictCursor,
                                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
    return connection