class Comment:
    def __init__(self, comment, created_by, created_on):
        self.__comment = comment
        self.__created_by = created_by
        self.__created_on = created_on

    def to_dict(self):
        comment_dict = {
            "comment": self.__comment,
            "created_by": self.__created_by,
            "created_on": self.__created_on
        }
        return comment_dict

    @property
    def comment(self):
        return self.__comment

    @property
    def created_by(self):
        return self.__created_by

    @property
    def created_on(self):
        return self.__created_on
