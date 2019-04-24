# File for all asset related functions
from db import dbc
from bson.objectid import ObjectId
import json


class Assets:
    @staticmethod
    def create(account, data):
        # Mongodb
        mongo = dbc()
        assets = mongo.db.assets
        #check if the account has access to the organization
        if data['org_id'] in account['orgs']:
            _id = assets.insert_one(data)
            return True, ["Asset created successfully",str(_id.inserted_id)]

        return False, "Account does not have access to the organization"


    @staticmethod
    def update(account, asset_id, data):
        # Mongo
        db = dbc().db
        assets = db.assets
        asset = assets.find_one({"_id": ObjectId(asset_id)})
        #check if the account has access to the organization
        if asset['org_id'] in account['orgs']:
            #if the organization is being updated
            try:
                #check if the account has the new organization
                if data['org_id'] in account['orgs']:
                    assets.update({"_id": ObjectId(asset_id)}, {"$set": data})
                    return True,"Success!"
                else:
                    return False, "Account does not have access to the new organization"
            #we get here if the data['org_id'] was not set so
            except NameError:
                #no change in the organization 
                assets.update({"_id": ObjectId(asset_id)}, {"$set": data})
                return True,"Success!"
        else:
            return False, "Account does not have access to this asset"

    @staticmethod
    def delete(account, asset_id):
        # Mongo
        db = dbc().db
        assets = db.assets
        asset = assets.find_one({"_id": ObjectId(asset_id)})
        #check if the account has access to the organization
        if asset['org_id'] in account['orgs']:
            assets.remove({"_id": ObjectId(asset_id)})
            return True,"Success!"

        return False, "Account does not have access to this asset"

    @staticmethod
    def get(account, asset_id):
        # Mongo
        db = dbc().db
        assets = db.assets
        asset = assets.find_one({"_id": ObjectId(asset_id)})
        #check if the account has access to the organization
        if asset['org_id'] in account['orgs']:
            asset['id'] = str(asset['_id'])
            del asset['_id']
            return True,asset
            
        return False, "Account does not have access to this asset"

    @staticmethod
    def getAll(account):
        # Mongo
        db = dbc().db
        assets = db.assets
        cursor = assets.find({})
        allAssets = []
        for asset in cursor:
            if asset['org_id'] in account['orgs']:
                asset['_id'] = str(asset['_id'])
                allAssets.append(asset)

        if len(allAssets) == 0:
            return False,"No assets accessible to this account found"

        return True,allAssets
