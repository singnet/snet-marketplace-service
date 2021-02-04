class CTA(object):
    def __init__(self, id, text, url, type, variant,
                 rank):
        self.__id = id
        self.__text = text
        self.__url = url
        self.__type = type
        self.__variant = variant
        self.__rank = rank

    @property
    def id(self):
        return self.__id

    @property
    def text(self):
        return self.__text

    @property
    def url(self):
        return self.__url

    @property
    def type(self):
        return self.__type

    @property
    def variant(self):
        return self.__variant

    @property
    def rank(self):
        return self.__rank

    def to_dict(self):
        response = {
            "id": self.id,
            "text": self.text,
            "url": self.url,
            "type": self.type,
            "rank": self.rank
        }

        return response
