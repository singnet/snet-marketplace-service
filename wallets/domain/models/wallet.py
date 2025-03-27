

class WalletModel:

    def __init__(self, row_id, address, type, encrypted_key, status):
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

