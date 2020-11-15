class ServiceComment:
    def __init__(self, org_uuid, service_uuid, support_type, user_type, commented_by, comment):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._support_type = support_type
        self._user_type = user_type
        self._commented_by = commented_by
        self._comment = comment

    def to_dict(self):
        return {
            "org_uuid": self._org_uuid,
            "service_uuid": self._service_uuid,
            "support_type": self._support_type,
            "user_type": self._user_type,
            "commented_by": self._commented_by,
            "comment": self._comment
        }

    @property
    def support_type(self):
        return self._support_type

    @property
    def user_type(self):
        return self._user_type

    @property
    def commented_by(self):
        return self._commented_by

    @property
    def comment(self):
        return self._comment

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def service_uuid(self):
        return self._service_uuid
