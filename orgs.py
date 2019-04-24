# File for all org related functions
from db import dbc
from bson.objectid import ObjectId
import json


class Orgs:
    @staticmethod
    def create(data):
        # Mongodb
        mongo = dbc()
        orgs = mongo.db.orgs
        org = orgs.find_one({'name': data['name']})
        if org:
            return False, "Organization was not created, name already used"
        else:
            _id = orgs.insert_one(data)
        return True, ["Organization created successfully",str(_id.inserted_id)]

    @staticmethod
    def update(org_id, data):
        # Mongo
        db = dbc().db
        orgs = db.orgs
        orgs.update({"_id": ObjectId(org_id)}, {"$set": data})

        return True,"Success!"

    @staticmethod
    def delete(org_id):
        # Mongo
        db = dbc().db
        orgs = db.orgs
        orgs.remove({"_id": ObjectId(org_id)})

        return True,"Success!"

    @staticmethod
    def get(org_id):
        # Mongo
        db = dbc().db
        orgs = db.orgs
        org = orgs.find_one({"_id": ObjectId(org_id)})
        org['id'] = str(org['_id'])
        del org['_id']

        return True,org
