import base64
import secrets


class Group:
    def __init__(self, name, group_id, payment_address, payment_config):
        self.name = name
        self.group_id = group_id
        self.payment_address = payment_address
        self.payment_config = payment_config

    def to_metadata(self):
        return {
            "group_name": self.name,
            "group_id": self.group_id,
            "payment": {
                "payment_address": self.payment_address,
                "payment_expiration_threshold": self.payment_config["payment_expiration_threshold"],
                "payment_channel_storage_client": self.payment_config["payment_channel_storage_client"]
            }
        }

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.group_id,
            "payment_address": self.payment_address,
            "payment_config": self.payment_config
        }

    def setup_id(self):
        if self.group_id is None:
            self.group_id = base64.b64encode(secrets.token_bytes(32))

    def validate_draft(self):
        return True
