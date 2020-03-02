from verification.constants import VerificationType


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
