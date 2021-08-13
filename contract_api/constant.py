from enum import Enum

GET_ALL_SERVICE_OFFSET_LIMIT = 0
GET_ALL_SERVICE_LIMIT = 15


class ServiceAssetsRegex(Enum):
    DEMO_FILE_PATH = "(assets\/)[a-zA-Z0-9_]*(\/)[a-zA-Z0-9_]*(\/)(component.tar.gz)"
