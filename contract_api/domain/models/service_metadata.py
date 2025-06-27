from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewServiceMetadataDomain:
    service_row_id: int
    org_id: str
    service_id: str
    display_name: str
    description: str
    short_description: str
    url: str
    json: str
    model_hash: str
    encoding: str
    type: str
    mpe_address: str
    assets_url: dict
    assets_hash: dict
    service_rating: dict
    contributors: dict


@dataclass
class ServiceMetadataDomain(NewServiceMetadataDomain):
    row_id: int
    demo_component_available: bool
    ranking: int
    created_on: datetime
    updated_on: datetime

    def to_response(self) -> dict:
        return {
            "org_id": self.org_id,
            "service_id": self.service_id,
            "display_name": self.display_name,
            "description": self.description,
            "short_description": self.short_description,
            "demo_component_available": self.demo_component_available,
            "url": self.url,
            "json": self.json,
            "model_hash": self.model_hash,
            "encoding": self.encoding,
            "type": self.type,
            "mpe_address": self.mpe_address,
            "assets_url": self.assets_url,
            "assets_hash": self.assets_hash,
            "service_rating": self.service_rating,
            "ranking": self.ranking,
            "contributors": self.contributors,
        }

    def to_short_response(self) -> dict:
        return {
            "orgId": self.org_id,
            "serviceId": self.service_id,
            "displayName": self.display_name,
            "description": self.description,
            "shortDescription": self.short_description,
            "url": self.url,
            "rating": self.service_rating["rating"],
            "numberOfRatings": self.service_rating["number_of_ratings"],
            "contributors": self.contributors,
        }


class ServiceMetadata:
    def __init__(self, service_row_id, org_id, service_id, display_name, description, short_description,
                 demo_component_available, url, json, model_hash, encoding, type, mpe_address, assets_url,
                 assets_hash, service_rating, ranking, contributors):
        self._service_row_id = service_row_id
        self._org_id = org_id
        self._service_id = service_id
        self._display_name = display_name
        self._description = description
        self._short_description = short_description
        self._demo_component_available = demo_component_available
        self._url = url
        self._json = json
        self._model_hash = model_hash
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
    def demo_component_available(self):
        return self._demo_component_available

    @property
    def url(self):
        return self._url

    @property
    def json(self):
        return self._json

    @property
    def model_hash(self):
        return self._model_hash

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

    @demo_component_available.setter
    def demo_component_available(self, demo_component_available):
        self._demo_component_available = demo_component_available

    @url.setter
    def url(self, url):
        self._url = url

    @json.setter
    def json(self, json):
        self._json = json

    @model_hash.setter
    def model_hash(self, model_hash):
        self._model_hash = model_hash

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
