from common.utils import datetime_to_string


class Comment:
    def __init__(self, comment, created_by, created_at):
        self.__comment = comment
        self.__created_by = created_by
        self.__created_at = created_at

    def to_dict(self):
        comment_dict = {
            "comment": self.__comment,
            "created_by": self.__created_by,
            "created_at": "" if self.__created_at is None else datetime_to_string(self.__created_at)
        }
        return comment_dict

    @property
    def comment(self):
        return self.__comment

    @property
    def created_by(self):
        return self.__created_by

    @property
    def created_at(self):
        return self.__created_at
