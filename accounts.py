# File for all account related functions
from db import dbc
from bson.objectid import ObjectId
import json
import hashlib
import time
import datetime
import random


class Accounts:
    @staticmethod
    def create(data):
        # Mongodb
        mongo = dbc()
        accounts = mongo.db.accounts
        account = accounts.find_one({'email': data['email']})
        if account:
            return False, "Account was not created, email already used"
        else:
            data['password'] = Accounts.c_hash(data['password'])
            _id = accounts.insert_one(data)
        return True, ["Account created successfully",str(_id.inserted_id)]

    @staticmethod
    def update(account, data):
        # Mongo
        db = dbc().db
        accounts = db.accounts
        #check if the email has been already used
        if ('email' in data) and (data['email'] != account['email']):
            check_account = accounts.find_one({'email': data['email']})
            if check_account:
                return False, "Account was not updated, email already used"
        if 'password' in data: 
            data['password'] = Accounts.c_hash(data['password'])
        accounts.update({"_id": ObjectId(account['_id'])}, {"$set": data})

        return True,"Success!"

    @staticmethod
    def delete(account_id):
        # Mongo
        db = dbc().db
        accounts = db.accounts
        accounts.remove({"_id": ObjectId(account_id)})

        return True,"Success!"

    @staticmethod
    def get(account_id):
        # Mongo
        db = dbc().db
        accounts = db.accounts
        account = accounts.find_one({"_id": ObjectId(account_id)})
        account['id'] = str(account['_id'])
        del account['_id']
        del account['password']
        return True,account

    @staticmethod
    def login(data):
        data['password'] = Accounts.c_hash(data['password'])
        mongo = dbc()
        accounts = mongo.db.accounts
        account = accounts.find_one({'$and': [{'email': data['email'], 'password': data['password']}]})
        if account:
            now = datetime.datetime.now();
            user_hash = Accounts.c_hash(account['email'] + str(time.time()) + str(random.randint(1,10000)))
            #make sure to use push as method for MongoDB so we add this new session to the array of sessions
            result = accounts.update({'_id': account['_id']}, 
                {'$push': {'session_hashes': {'hash': user_hash, 'last_action': str(now)}}})
            if not result['updatedExisting']:
                return False, "Something went wrong"
            else:
                return True, user_hash
        else:
            return False, "Account does not exist"

    @staticmethod
    def logout(account_id, user_hash):
        mongo = dbc()
        accounts = mongo.db.accounts
        #the account should have been checked already, as it was got from the user hash supplied in the cookie
        result = accounts.update({'_id': account_id}, 
                {'$pull': {'session_hashes': {'hash': user_hash}}})
        return True, "Successfully logout"   

    @staticmethod
    def account_from_hash(user_hash):
        mongo = dbc()
        accounts = mongo.db.accounts
        return accounts.find_one(
           { 'session_hashes': { '$elemMatch': { 'hash': user_hash } } }
        )

    @staticmethod
    def c_hash(s):
        return hashlib.sha256(s).hexdigest()
