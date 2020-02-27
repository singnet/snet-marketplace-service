from uuid import uuid5

from verification.config import USER_REFERENCE_ID_NAMESPACE
from base64 import b64encode
from hashlib import sha1


def get_user_reference_id_from_username(username):
    return sha1(username.encode("utf-8")).hexdigest()


def generate_basic_auth(username, password):
    encoded_user_pass = b64encode(bytes(username + ':' + password, "utf-8")).decode("ascii")
    return f"Basic {encoded_user_pass}"
