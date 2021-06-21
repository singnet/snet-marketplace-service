class Service:
    def __init__(self, org_id, service_id, service_path, ipfs_hash, is_curated, service_email, service_metadata):
        self._org_id = org_id
        self._service_id = service_id
        self._service_path = service_path
        self._ipfs_hash = ipfs_hash
        self._is_curated = is_curated
        self._service_email = service_email
        self._service_metadata = service_metadata

    @property
    def org_id(self):
        return self._org_id

    @org_id.setter
    def org_id(self, org_id):
        self._org_id = org_id

    @property
    def service_id(self):
        return self._service_id

    @service_id.setter
    def service_id(self, service_id):
        self._service_id = service_id

    @property
    def service_path(self):
        return self._service_path

    @service_path.setter
    def service_path(self, service_path):
        self._service_path = service_path

    @property
    def ipfs_hash(self):
        return self._ipfs_hash

    @ipfs_hash.setter
    def ipfs_hash(self, ipfs_hash):
        self._ipfs_hash = ipfs_hash

    @property
    def is_curated(self):
        return self._is_curated

    @is_curated.setter
    def is_curated(self, is_curated):
        self._is_curated = is_curated

    @property
    def service_email(self):
        return self._service_email

    @service_email.setter
    def service_email(self, service_email):
        self._service_email = service_email

    @property
    def service_metadata(self):
        return self._service_metadata

    @service_metadata.setter
    def service_metadata(self, service_metadata):
        self._service_metadata = service_metadata



