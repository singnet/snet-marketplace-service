class ServiceMedia:
    def __init__(self, org_id, service_id, service_row_id, url, order, file_type, asset_type, alt_text, ipfs_url):
        self._service_row_id = service_row_id
        self._org_id = org_id
        self._service_id = service_id
        self._url = url
        self._order = order
        self._file_type = file_type
        self._asset_type = asset_type
        self._alt_text = alt_text
        self._ipfs_url = ipfs_url

    def to_dict(self):
        return {
            "service_row_id": self._service_row_id,
            "org_id": self._org_id,
            "service_id": self._service_id,
            "url": self._url,
            "order": self._order,
            "file_type": self._file_type,
            "asset_type": self._asset_type,
            "alt_text": self._alt_text,
            "ipfs_url": self._ipfs_url
        }

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
    def service_row_id(self):
        return self._service_row_id

    @service_row_id.setter
    def service_row_id(self, service_row_id):
        self._service_row_id = service_row_id

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, order):
        self._order = order

    @property
    def file_type(self):
        return self._file_type

    @file_type.setter
    def file_type(self, file_type):
        self._file_type = file_type

    @property
    def asset_type(self):
        return self._asset_type

    @asset_type.setter
    def asset_type(self, asset_type):
        self._asset_type = asset_type

    @property
    def alt_text(self):
        return self._alt_text

    @alt_text.setter
    def alt_text(self, alt_text):
        self._alt_text = alt_text

    @property
    def ipfs_url(self):
        return self._ipfs_url

    @ipfs_url.setter
    def ipfs_url(self, ipfs_url):
        self.ipfs_url = ipfs_url
