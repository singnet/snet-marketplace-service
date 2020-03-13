class ServiceReviewHistory:
    def __init__(self, org_uuid, service_uuid, service_metadata, state, reviewed_by, reviewed_on, created_on,
                 updated_on):
        self._org_uuid = org_uuid
        self._service_uuid = service_uuid
        self._service_metadata = service_metadata
        self._state = state
        self._reviewed_by = reviewed_by
        self._reviewed_on = reviewed_on
        self._created_on = created_on
        self._updated_on = updated_on

    def to_dict(self):
        return {
            "org_uuid": self._org_uuid,
            "service_uuid": self._service_uuid,
            "service_metadata": self._service_metadata,
            "state": self._state,
            "reviewed_by": self._reviewed_by,
            "reviewed_on": self._reviewed_on,
            "created_on": self._created_on,
            "updated_on": self._updated_on
        }

    @property
    def org_uuid(self):
        return self._org_uuid

    @property
    def service_uuid(self):
        return self._service_uuid

    @property
    def service_metadata(self):
        return self._service_metadata

    @property
    def state(self):
        return self._state

    @property
    def reviewed_by(self):
        return self._reviewed_by

    @property
    def reviewed_on(self):
        return self._reviewed_on

    @property
    def created_on(self):
        return self._created_on

    @property
    def updated_on(self):
        return self._updated_on
