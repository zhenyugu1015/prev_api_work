from pymongo import MongoClient
import os


class dbc:
    def __init__(self):
        db_host = os.environ['DB_HOST'] if "DB_HOST" in os.environ else "127.0.0.1"
        db = os.environ['DB_DB'] if "DB_DB" in os.environ else "db"
        db_user = os.environ['DB_USER'] if "DB_USER" in os.environ else "root"
        db_pass = os.environ['DB_PASS'] if "DB_PASS" in os.environ else "pass"

        # Mongo
        self.client = MongoClient("mongodb://"+db_user+":"+db_pass+"@"+db_host+":27017/")
        self.db = self.client[db]

    def __del__(self):
        self.client.close()
