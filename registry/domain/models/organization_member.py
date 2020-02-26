from uuid import uuid4

from common.utils import datetime_to_string


class OrganizationMember(object):
    def __init__(self, org_uuid, username, status, role, address=None,
                 invite_code=None, transaction_hash=None, invited_on=None, updated_on=None):
        self.__role = role
        self.__org_uuid = org_uuid
        self.__username = username
        self.__status = status
        self.__address = address
        self.__invite_code = invite_code
        self.__transaction_hash = transaction_hash
        self.__invited_on = invited_on
        self.__updated_on = updated_on

    @property
    def org_uuid(self):
        return self.__org_uuid

    @property
    def username(self):
        return self.__username

    @property
    def status(self):
        return self.__status

    @property
    def address(self):
        return self.__address

    @property
    def role(self):
        return self.__role

    @property
    def invite_code(self):
        return self.__invite_code

    @property
    def transaction_hash(self):
        return self.__transaction_hash

    @property
    def invited_on(self):
        return self.__invited_on

    @property
    def updated_on(self):
        return self.__updated_on

    def set_transaction_hash(self, transaction_hash):
        self.__transaction_hash = transaction_hash

    def __repr__(self):
        return "Item(%s, %s,%s)" % (self.address, self.username, self.role)

    def __eq__(self, other):
        if isinstance(other, OrganizationMember):
            return self.address == other.address and self.username == other.username and self.role == other.role
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    def to_response(self):
        member_dict = {
            "username": self.username,
            "address": self.address,
            "status": self.status,
            "role": self.role,
            "invited_on": "",
            "updated_on": ""
        }
        if self.invited_on is not None:
            member_dict["invited_on"] = datetime_to_string(self.invited_on)
        if self.updated_on is not None:
            member_dict["updated_on"] = datetime_to_string(self.updated_on)
        return member_dict

    def generate_invite_code(self):
        self.__invite_code = uuid4().hex

    def set_status(self, status):
        self.__status = status

    def set_invited_on(self, invited_on):
        self.__invited_on = invited_on

    def set_updated_on(self, updated_on):
        self.__updated_on = updated_on

    def set_role(self, role):
        self.__role = role
