
class CreateChannelEventModel:

    def __init__(self, row_id, payload, status):
        self.__row_id = row_id
        self.__payload = payload
        self.__status = status

    @property
    def row_id(self):
        return self.__row_id

    @property
    def payload(self):
        return self.__payload

    @property
    def status(self):
        return self.__status