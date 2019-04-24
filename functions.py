import logging
from accounts import Accounts

class FieldsException(Exception):
    pass

# Check the fields to a request
def check_fields(data, required_fields, optional_fields=list()):
    data_copy = dict(data).copy()
    # Remove cookies if included
    if "cookies" in data_copy:
        del data_copy['cookies']

    # Check required fields
    for required_field in required_fields:
        if required_field in data_copy:
            del data_copy[required_field]
        else:
            logging.error("Missing required field " + required_field + " in api call")
            raise FieldsException("Missing required field " + required_field + " in api call")

    # Remove optional fields
    for optional_field in optional_fields:
        if optional_field in data_copy:
            del data_copy[optional_field]

    # Check if no fields remain
    if len(data_copy) != 0:
        logging.error(str(len(data_copy))+" Eranous fields in api call")
        raise FieldsException(str(len(data_copy))+" Eranous fields in api call")

class AuthException(Exception):
    pass

#check if the user has supplied the hash so it is authenticated
#if authenticated returns the account logged in
def check_hash(cookies):
    if "hash" not in cookies:
        logging.error("No cookie hash supplied, please login")
        raise AuthException("No cookie hash supplied, please login")
    account = Accounts.account_from_hash(cookies['hash'])
    if account is None:
        logging.error("Invalid hash")
        raise AuthException("Invalid hash")
    return account

#check if the user has supplied the hash so it is authenticated
#if authenticated returns the account if not none
def check_hash_no_exception(cookies):
    if "hash" not in cookies:
        logging.error("No cookie hash supplied, please login")
        return None
    account = Accounts.account_from_hash(cookies['hash'])
    if account is None:
        logging.error("Invalid hash")
        return None
    return account

