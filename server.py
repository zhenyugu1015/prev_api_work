from flask import Flask
from flask import request
from flask import Response
from flask_cors import CORS
import socket
import json
import os

from pymongo import MongoClient
#import MySQLdb

from accounts import Accounts
from orgs import Orgs
from personnel import Personnel
from work_orders import WorkOrders
from assets import Assets
from db import dbc
from functions import *

import logging

app = Flask(__name__)

# Allow cross-origin if not in prod
if "FLASK_ENV" not in os.environ or os.environ['FLASK_ENV'] != "production":
    print "DEBUG MODE, allowing cross-origin requests"
    CORS(app, supports_credentials=True)
else:
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://"+os.environ['BASE_URL'],"https://"+os.environ['BASE_URL']]}})

@app.route('/',methods=["GET"])
def index():
    try:
        db = dbc()
        # Return hostname
        check_fields(request.data,[],[])
        return socket.gethostname()
    except FieldsException as e:
        return json.dumps({"success": 0, "message": str(e)})
    except Exception as e:
        return json.dumps({"success": 0, "message": "Something went wrong"})


@app.route('/account',endpoint='account',methods=["GET", "POST", "PUT", "DELETE"])
def index():
    #TODO refactor these methods because some of them already have the account
    #  they do not need to retrieve it from an id.
    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = Accounts.get(account['_id'])
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})    
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "POST":
        try:
            data = json.loads(request.data)
            check_fields(data,["name","email","password", "permissions", "orgs"],[])
            success,message = Accounts.create(data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "PUT":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,[],["name","email","password", "permissions","orgs"])
            success,message = Accounts.update(account, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})  
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "DELETE":
        try:
            account = check_hash(request.cookies)
            success,message = Accounts.delete(account['_id'])
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
        
        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})


@app.route('/accounts/<string:account_id>',endpoint='accounts/',methods=["GET","PUT","DELETE"])
def index(account_id=-1):
    #TODO check if the user has permissions to do these operations
    #these are used for testing right now
    if request.method == "GET":
        try:
            success,message = Accounts.get(account_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
    
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "PUT":
        try:
            data = json.loads(request.data)
            check_fields(data,[],["name","email","password", "permissions","orgs"])
            success,message = Accounts.update(account_id, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "DELETE":
        try:
            success,message = Accounts.delete(account_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
    
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})


@app.route('/account/login',endpoint='account/login',methods=["POST"])
def index():

    try:
        data = json.loads(request.data)
        check_fields(data,["email","password"],[])
        account = check_hash_no_exception(request.cookies)

        if account is not None:
            if account["email"] == data["email"]:
                return json.dumps({
                    "success": 0,
                    "message": "Already authenticated user"
                    })
            else: 
                # if the account is authenticated as another user, 
                # log him out and then log in as the other user 
                Accounts.logout(account['_id'], request.cookies['hash'])

        success,message = Accounts.login(data)
        if not success:
            return json.dumps({
                "success": 0,
                "message": message
                })
        else:
            body = json.dumps({
                "success": 1,
                "message": "Successfully logged in"
                })
            #print "almost done"
            resp = Response(body,status=200)
            resp.set_cookie('hash', value = message)
            return resp

    except FieldsException as e:
        return json.dumps({"success": 0, "message": str(e)})
    except Exception as e:
        return json.dumps({"success": 0, "message": str(e)})

@app.route('/account/logout',endpoint='account/logout',methods=["GET"])
def index():

    try:
        account = check_hash(request.cookies)
        success,message = Accounts.logout(account['_id'], request.cookies['hash'])
        if not success:
            return json.dumps({
                "success": 0,
                "message": message
                })
        else:
            body = json.dumps({
                "success": 1,
                "message": message
                })
            #print "almost done"
            resp = Response(body,status=200)
            #set a cookie that will expire in unixtime 0, which should be the past
            resp.set_cookie('hash', '', expires=0)
            return resp

    except Exception as e:
        return json.dumps({"success": 0, "message": str(e)})

@app.route('/org',endpoint='org',methods=["POST"])
def index():
    if request.method == "POST":
        try:
            data = json.loads(request.data)
            check_fields(data,["name"],[])
            success,message = Orgs.create(data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})


@app.route('/orgs/<string:org_id>',endpoint='orgs/',methods=["GET","PUT","DELETE"])
def index(org_id=-1):
    #TODO check if the user has permissions to do these operations
    if request.method == "GET":
        try:
            success,message = Orgs.get(org_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "PUT":
        try:
            data = json.loads(request.data)
            check_fields(data,["name"],[])
            success,message = Orgs.update(org_id, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
    
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "DELETE":
        try:
            success,message = Orgs.delete(org_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
    
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/asset',endpoint='asset',methods=["POST"])
def index():
    if request.method == "POST":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,["org_id"],["name","description","tags"])
            success,message = Assets.create(account,data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/assets',endpoint='assets',methods=["GET"])
def index():
    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = Assets.getAll(account)
            return json.dumps({"success": 1 if success else 0, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/assets/<string:asset_id>',endpoint='assets/',methods=["GET","PUT","DELETE"])
def index(asset_id=-1):
    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = Assets.get(account, asset_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "PUT":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,[],["org_id", "name", "description", "tags"])
            success,message = Assets.update(account, asset_id, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "DELETE":
        try:
            account = check_hash(request.cookies)
            success,message = Assets.delete(account, asset_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/personnel',endpoint='personnel',methods=["POST", "GET"])
def index():
    if request.method == "POST":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,["org_id", "name", "description", "tags"],[])
            success,message = Personnel.create(account,data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = Personnel.getAll(account)
            return json.dumps({"success": 1 if success else 0, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/personnel/<string:personnel_id>',endpoint='personnel/',methods=["GET","PUT","DELETE"])
def index(personnel_id=-1):
    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = Personnel.get(account, personnel_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
        
        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "PUT":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,[],["org_id", "name", "description", "tags"])
            success,message = Personnel.update(account,personnel_id, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
        
        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "DELETE":
        try:
            account = check_hash(request.cookies)
            success,message = Personnel.delete(account, personnel_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/work_order',endpoint='work_order',methods=["POST"])
def index():
    if request.method == "POST":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,["org_id", "name", "description"],["tags"])
            success,message = WorkOrders.create(account, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

@app.route('/work_orders',endpoint='work_orders',methods=["GET"])
def index():
    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = WorkOrders.getAll(account)
            return json.dumps({"success": 1 if success else 0, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": str(e)})


@app.route('/work_orders/<string:work_order_id>',endpoint='work_order/',methods=["GET","PUT","DELETE"])
def index(work_order_id=-1):
    if request.method == "GET":
        try:
            account = check_hash(request.cookies)
            success,message = WorkOrders.get(account, work_order_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "PUT":
        try:
            account = check_hash(request.cookies)
            data = json.loads(request.data)
            check_fields(data,[],["org_id","name", "description", "tags"])
            success,message = WorkOrders.update(account, work_order_id, data)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})

        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

    if request.method == "DELETE":
        try:
            account = check_hash(request.cookies)
            success,message = WorkOrders.delete(account, work_order_id)
            if not success:
                return json.dumps({"success": 0, "message": message})
            else:
                return json.dumps({"success": 1, "message": message})
    
        except AuthException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except FieldsException as e:
            return json.dumps({"success": 0, "message": str(e)})
        except Exception as e:
            logging.error(str(e))
            return json.dumps({"success": 0, "message": "Something went wrong"})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
