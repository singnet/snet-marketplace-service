from enum import Enum


class OrganizationStatus(Enum):
    DRAFT = "DRAFT"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPROVED = "APPROVED"
    PUBLISH_IN_PROGRESS = "PUBLISH_IN_PROGRESS"
    PUBLISHED = "PUBLISHED"
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

