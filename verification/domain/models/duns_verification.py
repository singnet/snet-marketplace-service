import json
from datetime import datetime

from common.utils import datetime_to_string
from verification.constants import DUNSVerificationStatus


class DUNSVerification:
    def __init__(self, verification_id, org_uuid, status, comments, created_at, update_at):
        self.verification_id = verification_id
        self.org_uuid = org_uuid
        self.status = status
        self.comments = comments
        self.created_at = created_at
        self.updated_at = update_at

    def initiate(self):
        self.status = DUNSVerificationStatus.PENDING.value
        current_time = datetime.utcnow()
        self.created_at = current_time
        self.updated_at = current_time

    def update_callback(self, verification_payload):
        verification_details = json.loads(verification_payload)
        self.add_comment(verification_details["comment"], verification_details["reviewed_by"])
        status = verification_details["verificationStatus"]
        if status not in [DUNSVerificationStatus.PENDING.value, DUNSVerificationStatus.APPROVED.value,
                          DUNSVerificationStatus.REJECTED.value, DUNSVerificationStatus.CHANGE_REQUESTED.value]:
            raise Exception("Invalid status for verification")

        self.status = status
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        verification_dict = {
            "verification_id": self.verification_id,
            "org_uuid": self.org_uuid,
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
