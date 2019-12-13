
class Group:
    def __init__(self, group_name, group_id, payment_address, payment_config):
        self.name = group_name
        self.group_id = group_id
        self.payment_address = payment_address
        self.payment_config = payment_config

    def to_dict(self):
        return {
            "group_name": self.group_name,
            "group_id": self.group_id
        }
