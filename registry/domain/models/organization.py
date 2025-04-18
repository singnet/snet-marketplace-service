from typing import Any, List
from uuid import uuid4
from dataclasses import dataclass, field

from deepdiff import DeepDiff

from common.exceptions import OperationNotAllowed
from common.logger import get_logger
from common.utils import datetime_to_string
from registry.constants import OrganizationActions, OrganizationAddressType, OrganizationStatus, OrganizationType
from registry.domain.models.organization_address import OrganizationAddress
from registry.infrastructure.storage_provider import get_storage_provider_by_uri

logger = get_logger(__name__)

BLOCKCHAIN_EXCLUDE_PATHS = [
    "root._Organization__uuid", "root._Organization__duns_no",
    "root._Organization__registration_id", "root._Organization__registration_type", "root._Organization__origin",
    "root._Organization__state", "root._Organization__addresses",
    "root._Organization__assets['hero_image']['url']"]

BLOCKCHAIN_EXCLUDE_REGEX_PATH = ["root\._Organization__groups\[.*\]\.status"]

ORGANIZATION_MINOR_CHANGES = [
    "root._Organization__state", "root._Organization__assets['hero_image']['url']",
    "root._Organization__assets['hero_image']['ipfs_hash']", "root._Organization__metadata_ipfs_uri",
    "root._Organization__contacts", "root._Organization__registration_id", "root._Organization__registration_type"]

GROUP_MINOR_CHANGES = [
    "root\._Organization__groups\[.*\]\.status",
    "root\._Organization__groups\[.*\]\.name",
    "root\._Organization__groups\[.*\]\.payment_config",
    "root\._Organization__groups\[.*\]\.payment_config\[\'payment_channel_storage_type\'\]",
    "root\._Organization__groups\[.*\]\.payment_config\[\'payment_channel_storage_client\'\]\[\'connection_timeout\'\]",
    "root\._Organization__groups\[.*\]\.payment_config\[\'payment_channel_storage_client\'\]\[\'request_timeout\'\]",
    "root\._Organization__groups\[.*\]\.payment_config\[\'payment_channel_storage_client\'\]\[\'endpoints\'\]"
]


@dataclass
class Organization:
    uuid: str
    id: str
    name: str
    org_type: str
    origin: str
    description: str
    short_description: str
    url: str
    contacts: list
    assets: dict
    metadata_uri: str
    duns_no: str
    groups: List[Any]
    addresses: list
    org_state: Any
    members: List[Any] = field(default_factory=list)

    def to_metadata(self):
        ipfs_uri_prefix = "ipfs://"
        filecoin_uri_prefix = "filecoin://"
        result_assets = {}

        for key, asset in self.assets.items():
            hash_uri = asset.get("ipfs_hash") or asset.get("hash", "")
            if not hash_uri.startswith(ipfs_uri_prefix) and not hash_uri.startswith(filecoin_uri_prefix):
                hash_uri = ipfs_uri_prefix + hash_uri
            result_assets[key] = hash_uri

        return {
            "org_name": self.name,
            "org_id": self.id,
            "org_type": self.org_type,
            "description": {
                "description": self.description,
                "short_description": self.short_description,
                "url": self.url
            },
            "contacts": self.contacts,
            "assets": result_assets,
            "groups": [group.to_metadata() for group in self.groups]
        }

    def to_response(self):
        head_quarter_address = None
        mail_address = None
        mail_address_same_hq_address = False

        for address in self.addresses:
            if address.address_type == OrganizationAddressType.MAIL_ADDRESS.value:
                mail_address = address
            elif address.address_type == OrganizationAddressType.HEAD_QUARTER_ADDRESS.value:
                head_quarter_address = address

        if mail_address and head_quarter_address and mail_address == head_quarter_address:
            mail_address_same_hq_address = True

        return {
            "org_name": self.name,
            "org_id": self.id,
            "org_uuid": self.uuid,
            "org_type": self.org_type,
            "description": self.description,
            "short_description": self.short_description,
            "url": self.url,
            "duns_no": self.duns_no,
            "origin": self.origin,
            "contacts": self.contacts,
            "assets": self.assets,
            "metadata_uri": self.metadata_uri,
            "storage_provider": get_storage_provider_by_uri(self.metadata_uri),
            "groups": [group.to_response() for group in self.groups],
            "org_address": {
                "mail_address_same_hq_address": mail_address_same_hq_address,
                "addresses": [address.to_response() for address in self.addresses]
            },
            "state": self.org_state.to_response() if isinstance(self.org_state, OrganizationState) else {}
        }

    def setup_id(self):
        self.uuid = uuid4().hex
        if self.org_type == OrganizationType.INDIVIDUAL.value:
            self.id = self.uuid

    def is_org_id_set(self):
        return not self.id or len(self.id) == 0

    def is_org_uuid_set(self):
        return not self.uuid or len(self.uuid) == 0

    def is_valid_field(self, field):
        return bool(field and len(field) > 0)

    def is_valid(self):
        return all([
            self.is_valid_field(self.name),
            self.is_valid_field(self.uuid),
            self.is_valid_field(self.id),
            self.is_valid_field(self.org_type),
            len(self.groups) > 0
        ])

    def is_blockchain_major_change(self, updated_organization):
        diff = DeepDiff(self, updated_organization,
                        exclude_types=[OrganizationAddress, OrganizationState],
                        exclude_paths=BLOCKCHAIN_EXCLUDE_PATHS,
                        exclude_regex_paths=BLOCKCHAIN_EXCLUDE_REGEX_PATH)
        logger.info(f"DIff for metadata organization {diff}")
        return bool(diff), diff

    def is_major_change(self, updated_organization):
        diff = DeepDiff(self, updated_organization,
                        exclude_types=[OrganizationState],
                        exclude_paths=ORGANIZATION_MINOR_CHANGES,
                        exclude_regex_paths=GROUP_MINOR_CHANGES)
        logger.info(f"DIff for metadata organization {diff}")
        return bool(diff), diff

    @staticmethod
    def next_state(current_organization, updated_organization, action):
        if action in {OrganizationActions.DRAFT.value, OrganizationActions.SUBMIT.value}:
            return Organization.next_state_for_update(current_organization, updated_organization)
        elif action == OrganizationActions.CREATE.value:
            return OrganizationStatus.ONBOARDING_APPROVED.value
        else:
            raise Exception("Invalid Action for Organization")

    @staticmethod
    def next_state_for_update(current_organization, updated_organization):
        status = current_organization.get_status()
        if status in {OrganizationStatus.CHANGE_REQUESTED.value, OrganizationStatus.ONBOARDING.value}:
            return OrganizationStatus.ONBOARDING_APPROVED.value
        elif status in {OrganizationStatus.APPROVED.value, OrganizationStatus.PUBLISHED.value}:
            return OrganizationStatus.APPROVED.value
        elif status == OrganizationStatus.ONBOARDING_APPROVED.value:
            return OrganizationStatus.ONBOARDING_APPROVED.value
        elif status == OrganizationStatus.APPROVAL_PENDING.value:
            return OrganizationStatus.APPROVED.value
        else:
            raise OperationNotAllowed()

    def get_status(self):
        return self.org_state.state if self.org_state else None

    def _get_all_contact_for_organization(self):
        return list({c['email_id'] for c in self.contacts if 'email_id' in c})


@dataclass
class OrganizationState:
    org_uuid: str
    state: str
    transaction_hash: str | None
    wallet_address: str | None
    created_by: str | None
    updated_by: str | None
    reviewed_by: str | None
    reviewed_on: str | None
    comments: List[Any]

    updated_on: str | None
    created_on: str| None

    
    def to_response(self):
        state_dict = {
            "state": self.state,
            "updated_on": "",
            "updated_by": self.updated_by,
            "reviewed_by": self.reviewed_by,
            "reviewed_on": "",
            "comments": self.comment_dict_list()
        }

        if self.updated_on is not None:
            state_dict["updated_on"] = datetime_to_string(self.updated_on)
        if self.reviewed_on is not None:
            state_dict["reviewed_on"] = datetime_to_string(self.reviewed_on)

        return state_dict

    def comment_dict_list(self):
        self.comments.sort(key=lambda x: x.created_on, reverse=True)
        return [comment.to_dict() for comment in self.comments]

    def get_latest_comment(self):
        if len(self.comments) == 0:
            return None
        self.comments.sort(key=lambda x: x.created_on, reverse=True)
        return self.comments[0].comment

    def to_dict(self):
        state_dict = {
            "state": self.state,
            "transaction_hash": self.transaction_hash,
            "wallet_address": self.wallet_address,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "reviewed_by": self.reviewed_by,
            "reviewed_on": "",
            "created_on": "",
            "updated_on": ""
        }

        if self.updated_on is not None:
            state_dict["updated_on"] = datetime_to_string(self.updated_on)
        if self.reviewed_on is not None:
            state_dict["reviewed_on"] = datetime_to_string(self.reviewed_on)
        if self.created_on is not None:
            state_dict["created_on"] = datetime_to_string(self.created_on)

        return state_dict