from uuid import uuid5

from verification.config import USER_REFERENCE_ID_NAMESPACE
from base64 import b64encode

def get_user_reference_id_from_username(username):
    return uuid5(USER_REFERENCE_ID_NAMESPACE, username)

def generate_basic_auth(username, password):
    encoded_user_pass = b64encode(bytes(username + ':' + password, "utf-8")).decode("ascii")
    return f"Basic {encoded_user_pass}"