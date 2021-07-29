class ServiceMetadata:
    def __init__(self, service_row_id, org_id, service_id, display_name, description, short_description, url, json, model_ipfs_hash, encoding, type, mpe_address, assets_url,
                 assets_hash, service_rating, ranking, contributors):
        self._service_row_id = service_row_id
        self._org_id = org_id
        self._service_id = service_id
        self._display_name = display_name
        self._description = description
        self._short_description = short_description
        self._url = url
        self._json = json
        self._model_ipfs_hash = model_ipfs_hash
        self._encoding = encoding
        self._type = type
        self._mpe_address = mpe_address
        self._assets_url = assets_url
        self._assets_hash = assets_hash
        self._service_rating = service_rating
        self._ranking = ranking
        self._contributors = contributors

    @property
    def service_row_id(self):
        return self._service_row_id

    @property
    def org_id(self):
        return self._org_id

    @property
    def service_id(self):
        return self._service_id

    @property
    def display_name(self):
        return self._display_name

    @property
    def description(self):
        return self._description

    @property
    def short_description(self):
        return self._short_description

    @property
    def url(self):
        return self._url

    @property
    def json(self):
        return self._json

    @property
    def model_ipfs_hash(self):
        return self._model_ipfs_hash

    @property
    def encoding(self):
        return self._encoding

    @property
    def type(self):
        return self._type

    @property
    def mpe_address(self):
        return self._mpe_address

    @property
    def assets_url(self):
        return self._assets_url

    @property
    def assets_hash(self):
        return self._assets_hash

    @property
    def service_rating(self):
        return self._service_rating

    @property
    def ranking(self):
        return self._ranking

    @property
    def contributors(self):
        return self._contributors

    @service_row_id.setter
    def service_row_id(self, service_row_id):
        self._service_row_id = service_row_id

    @org_id.setter
    def org_id(self, org_id):
        self._org_id = org_id

    @service_id.setter
    def service_id(self, service_id):
        self._service_id = service_id

    @display_name.setter
    def display_name(self, display_name):
        self._display_name = display_name

    @description.setter
    def description(self, description):
        self._description = description

    @short_description.setter
    def short_description(self, short_description):
        self._short_description = short_description

    @url.setter
    def url(self, url):
        self._url = url

    @json.setter
    def json(self, json):
        self._json = json

    @model_ipfs_hash.setter
    def model_ipfs_hash(self, model_ipfs_hash):
        self._model_ipfs_hash = model_ipfs_hash

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    @type.setter
    def type(self, type):
        self._type = type

    @mpe_address.setter
    def mpe_address(self, mpe_address):
        self._mpe_address = mpe_address

    @assets_url.setter
    def assets_url(self, assets_url):
        self._assets_url = assets_url

    @assets_hash.setter
    def assets_hash(self, assets_hash):
        self._assets_hash = assets_hash

    @service_rating.setter
    def service_rating(self, service_rating):
        self._service_rating = service_rating

    @ranking.setter
    def ranking(self, ranking):
        self._ranking = ranking

    @contributors.setter
    def contributors(self, contributors):
        self._contributors = contributors
