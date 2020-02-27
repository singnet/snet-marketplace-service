import os
from enum import Enum

COMMON_CNTRCT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'node_modules', 'singularitynet-platform-contracts'))
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/Registry.json'
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/MultiPartyEscrow.json'
REG_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/Registry.json'
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/MultiPartyEscrow.json'


class OrganizationStatus(Enum):
    DRAFT = "DRAFT"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    PUBLISH_IN_PROGRESS = "PUBLISH_IN_PROGRESS"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    PUBLISHED_UNAPPROVED = "PUBLISHED_UNAPPROVED"


class AddOrganizationActions(Enum):
    DRAFT = "DRAFT"
    SUBMIT = "SUBMIT"


class OrganizationMemberStatus(Enum):
    PUBLISHED = "PUBLISHED"
    PENDING = "PENDING"
    PUBLISH_IN_PROGRESS = "PUBLISH_IN_PROGRESS"
    ACCEPTED = "ACCEPTED"


class Role(Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


class Action(Enum):
    CREATE = "CREATE"
    SUBMIT = "SUBMIT"
    PUBLISH = "PUBLISH"
    UPDATE = "UPDATE"
    READ = "READ"


class ServiceAvailabilityStatus(Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class ServiceStatus(Enum):
    DRAFT = "DRAFT"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    PUBLISH_IN_PROGRESS = "PUBLISH_IN_PROGRESS"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
    PUBLISHED_UNAPPROVED = "PUBLISHED_UNAPPROVED"


class OrganizationAddressType(Enum):
    MAIL_ADDRESS = "mailing_address"
    HEAD_QUARTER_ADDRESS = "headquarter_address"


DEFAULT_SERVICE_RANKING = 1
