import json
from datetime import datetime

from common.utils import datetime_to_string
from verification.constants import IndividualVerificationStatus
from verification.domain.models.comment import Comment


class IndividualVerification:
    def __init__(self, verification_id, username, status, comments, created_at, updated_at):
        self.verification_id = verification_id
        self.username = username
        self.status = status
        self.comments = comments
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def initiate(cls, verification_id, username):
        current_time = datetime.utcnow()
        return cls(verification_id, username, IndividualVerificationStatus.PENDING.value,
                   [], current_time, current_time)

    def approve(self):
        self.status = IndividualVerificationStatus.APPROVED.value

    def to_dict(self):
        verification_dict = {
            "verification_id": self.verification_id,
            "username": self.username,
            "status": self.status,
            "comments": self.comment_dict_list(),
            "created_at": "",
            "updated_at": ""
        }
        if self.created_at is not None:
            verification_dict["created_at"] = datetime_to_string(self.created_at)
        if self.updated_at is not None:
            verification_dict["updated_at"] = datetime_to_string(self.updated_at)
        return verification_dict

    def comment_dict_list(self):
        self.sort_comments()
        return [comment.to_dict() for comment in self.comments]

    def sort_comments(self):
        self.comments.sort(key=lambda x: x.created_at, reverse=True)

    def add_comment(self, comment, username):
        self.comments.append(
            Comment(comment, username, datetime_to_string(datetime.utcnow()))
        )

    def update_callback(self, verification_payload):
        verification_details = json.loads(verification_payload)
        self.add_comment(verification_details["comment"], verification_details["reviewed_by"])
        status = verification_details["verificationStatus"]
        if status not in [IndividualVerificationStatus.PENDING.value, IndividualVerificationStatus.APPROVED.value,
                          IndividualVerificationStatus.REJECTED.value, IndividualVerificationStatus.CHANGE_REQUESTED.value]:
            raise Exception("Invalid status for verification")

        self.status = status
        self.updated_at = datetime.utcnow()
