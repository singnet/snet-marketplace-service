
class UserWalletModel:

    def __init__(self, row_id, username, address, is_default):
        self.__row_id = row_id
        self.__username = username
        self.__address = address
        self.__is_default = is_default

    @property
    def row_id(self):
        return self.__row_id

    @property
    def username(self):
        return self.__username

    @property
    def address(self):
        return self.__address

    @property
    def is_default(self):
        return self.__is_default

    def to_dict(self) -> dict:
        return {
            "row_id": self.__row_id,
            "username": self.__username,
            "address": self.__address,
            "is_default": self.__is_default
        }