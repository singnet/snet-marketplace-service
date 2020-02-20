from verification.config import USER_REFERENCE_ID_NAMESPACE
from uuid import uuid4, uuid5


def get_user_reference_id_from_username(username):
    return uuid5(USER_REFERENCE_ID_NAMESPACE, username)
