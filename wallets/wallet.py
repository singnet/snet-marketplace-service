class Wallet:
    def __init__(self, address, type, private_key=None, status=None):
        self.__address = address
        self.__private_key = private_key
        self.__status = status
        self.__type = type

    @property
    def address(self):
        return self.__address

    @property
    def private_key(self):
        return self.__private_key

    @property
    def status(self):
        return self.__status

    @property
    def type(self):
        return self.__type

    def to_dict(self):
        return {"address": self.address, "private_key": self.private_key, "status": self.status,
                "type": self.type}
