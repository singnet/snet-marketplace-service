from common.utils import datetime_to_string


class Verification:
    def __init__(self, id, type, entity_id, status, requestee, created_at, updated_at, jumio=None):
        self.id = id
        self.type = type
        self.entity_id = entity_id
        self.status = status
        self.requestee = requestee
        self.created_at = created_at
        self.updated_at = updated_at
        self.jumio = jumio

    def set_jumio(self, jumio):
        self.jumio = jumio

    def to_response(self):
        response_dict = {
            "id": self.id,
            "type": self.type,
            "entity_id": self.entity_id,
            "status": self.status,
            "requestee": self.requestee,
            "created_at": "",
            "updated_at": "",
        }
        if self.created_at is not None:
            response_dict["created_at"] = datetime_to_string(self.created_at)
        if self.updated_at is not None:
            response_dict["updated_at"] = datetime_to_string(self.updated_at)
        return response_dict
