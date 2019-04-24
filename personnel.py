# File for all org related functions
from db import dbc
from bson.objectid import ObjectId
import json


class Personnel:
    @staticmethod
    def create(account, data):
        # Mongodb
        mongo = dbc()
        personnel = mongo.db.personnel
        #check if the account has access to the organization
        if data['org_id'] in account['orgs']:
            single_personnel = personnel.find_one({'$and': [{'name': data['name'], 'org_id': data['org_id']}]})
            if single_personnel:
                return False, "Personnel was not created, name and org_id already used"
            else:
                _id = personnel.insert_one(data)
            return True, ["Personnel created successfully",str(_id.inserted_id)]
        return False, "Account does not have access to the organization"

    @staticmethod
    def update(account, single_personnel_id, data):
        # Mongo
        db = dbc().db
        personnel = db.personnel
        single_personnel = personnel.find_one({"_id": ObjectId(single_personnel_id)})
        #check if the account has access to the organization
        if single_personnel['org_id'] in account['orgs']:
            #if the organization is being updated
            try:
                #check if the account has that organization
                if data['org_id'] in account['orgs']:
                    personnel.update({"_id": ObjectId(single_personnel_id)}, {"$set": data})
                    return True,"Success!"
                else:
                    return False, "Account does not have access to the new organization"
            #we get here if the data['org_id'] was not set so
            except NameError:
                #no change in the organization 
                personnel.update({"_id": ObjectId(single_personnel_id)}, {"$set": data})
                return True,"Success!"
        else:
            return False, "Account does not have access to this personnel"


    @staticmethod
    def delete(account, single_personnel_id):
        # Mongo
        db = dbc().db
        personnel = db.personnel
        single_personnel = personnel.find_one({"_id": ObjectId(single_personnel_id)})
        #check if the account has access to the organization
        if single_personnel['org_id'] in account['orgs']:
            personnel.remove({"_id": ObjectId(single_personnel_id)})
            return True,"Success!"

        return False, "Account does not have access to this personnel"

    @staticmethod
    def get(account, single_personnel_id):
        # Mongo
        db = dbc().db
        personnel = db.personnel
        single_personnel = personnel.find_one({"_id": ObjectId(single_personnel_id)})
        #check if the account has access to the organization
        if single_personnel['org_id'] in account['orgs']:
            single_personnel['id'] = str(single_personnel['_id'])
            del single_personnel['_id']
            return True,single_personnel
            
        return False, "Account does not have access to this personnel"

    @staticmethod
    def getAll(account):
        # Mongo
        db = dbc().db
        personnel = db.personnel
        cursor = personnel.find({})
        allPersonnel = []
        for person in cursor:
            if person['org_id'] in account['orgs']:
                person['_id'] = str(person['_id'])
                allPersonnel.append(person)

        if len(allPersonnel) == 0:
            return False,"No personnel accessible to this account found"

        return True,allPersonnel
