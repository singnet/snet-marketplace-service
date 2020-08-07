import json
from datetime import datetime

from common.utils import datetime_to_string
from verification.constants import IndividualVerificationStatus
from verification.domain.models.comment import Comment


class IndividualVerification:
    def __init__(self, verification_id, username, status, comments, created_at, updated_at):
        self.__verification_id = verification_id
        self.__username = username
        self.__status = status
        self.__comments = comments
        self.__created_at = created_at
        self.__updated_at = updated_at

    @property
    def verification_id(self):
        return self.__verification_id

    @property
    def username(self):
        return self.__username

    @property
    def status(self):
        return self.__status

    @property
    def comments(self):
        return self.__comments

    @property
    def created_at(self):
        return self.__created_at

    @property
    def updated_at(self):
        return self.__updated_at

    @classmethod
    def initiate(cls, verification_id, username):
        current_time = datetime.utcnow()
        return cls(verification_id, username, IndividualVerificationStatus.PENDING.value,
                   [], current_time, current_time)

    def approve(self):
        self.__status = IndividualVerificationStatus.APPROVED.value

    def to_dict(self):
        verification_dict = {
            "verification_id": self.__verification_id,
            "username": self.__username,
            "status": self.__status,
            "comments": self.comment_dict_list(),
            "created_at": "",
            "updated_at": ""
        }
        if self.__created_at is not None:
            verification_dict["created_at"] = datetime_to_string(self.__created_at)
        if self.__updated_at is not None:
            verification_dict["updated_at"] = datetime_to_string(self.__updated_at)
        return verification_dict

    def comment_dict_list(self):
        self.sort_comments()
        return [comment.to_dict() for comment in self.__comments]

    def sort_comments(self):
        self.__comments.sort(key=lambda x: x.created_at, reverse=True)

    def add_comment(self, comment, username):
        self.__comments.append(
            Comment(comment, username, datetime_to_string(datetime.utcnow()))
        )

    def update_callback(self, verification_payload):
        verification_details = json.loads(verification_payload)
        self.add_comment(verification_details["comment"], verification_details["reviewed_by"])
        status = verification_details["verificationStatus"]
        if status not in [IndividualVerificationStatus.PENDING.value, IndividualVerificationStatus.APPROVED.value,
                          IndividualVerificationStatus.REJECTED.value,
                          IndividualVerificationStatus.CHANGE_REQUESTED.value]:
            raise Exception("Invalid status for verification")

        self.__status = status
        self.__updated_at = datetime.utcnow()
