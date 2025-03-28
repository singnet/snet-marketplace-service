

class WalletModel:

    def __init__(self, address, type, status, encrypted_key=None, row_id=None):
        self.__row_id = row_id
        self.__address = address
        self.__type = type
        self.__encrypted_key = encrypted_key
        self.__status = status

    @property
    def row_id(self):
        return self.__row_id

    @property
    def address(self):
        return self.__address

    @property
    def type(self):
        return self.__type

    @property
    def encrypted_key(self):
        return self.__encrypted_key

    @property
    def status(self):
        return self.__status

    def to_dict(self):
        return {
            "row_id": self.__row_id,
            "address": self.__address,
            "type": self.__type,
            "encrypted_key": self.__encrypted_key,
            "status": self.__status
        }

    def to_response(self):
        return {
            "address": self.__address,
            "type": self.__type,
            "private_key": None,
            "status": self.__status
        }

