class Banner(object):
    def __init__(self, id, image, image_alignment, alt_text, title,
                 rank, description):
        self.__id = id
        self.__image = image
        self.__image_alignment = image_alignment
        self.__alt_text = alt_text
        self.__title = title
        self.__rank = rank
        self.__description = description
        # self.__row_created = row_created
        # self.__row_updated = row_updated

    @property
    def id(self):
        return self.__id

    @property
    def image(self):
        return self.__image

    @property
    def image_alignment(self):
        return self.__image_alignment

    @property
    def alt_text(self):
        return self.__alt_text

    @property
    def title(self):
        return self.__title

    @property
    def rank(self):
        return self.__rank

    @property
    def description(self):
        return self.__description

    # @property
    # def row_created(self):
    #     return self.__row_created
    #
    # @property
    # def row_updated(self):
    #     return self.__row_updated

    def to_response(self):
        response = {
            "id": self.id,
            "image": self.image,
            "alt_text": self.alt_text,
            "image_alignment": self.image_alignment,
            "title": self.title,
            "description": self.description,
            # "row_created": self.row_created,
            # "row_updated": self.row_updated
        }
        # if self.row_created is not None:
        #     response["row_created"] = datetime_to_string(self.row_created)
        # if self.row_updated is not None:
        #     response["row_created"] = datetime_to_string(self.row_updated)
        return response
