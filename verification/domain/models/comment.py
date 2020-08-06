class Comment:
    def __init__(self, comment, created_by, created_at):
        self.comment = comment
        self.created_by = created_by
        self.created_at = created_at

    def to_dict(self):
        comment_dict = {
            "comment": self.comment,
            "created_by": self.created_by,
            "created_at": self.created_at
        }
        return comment_dict
