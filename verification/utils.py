from uuid import uuid5

from verification.config import USER_REFERENCE_ID_NAMESPACE


def get_user_reference_id_from_username(username):
    return uuid5(USER_REFERENCE_ID_NAMESPACE, username)
