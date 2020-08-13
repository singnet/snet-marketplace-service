from enum import Enum

class DUNSVerificationStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGE_REQUESTED = "CHANGE_REQUESTED"


class IndividualVerificationStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGE_REQUESTED = "CHANGE_REQUESTED"


class VerificationStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    CHANGE_REQUESTED = "CHANGE_REQUESTED"


class VerificationType(Enum):
    JUMIO = "JUMIO"
    DUNS = "DUNS"
    INDIVIDUAL = "INDIVIDUAL"

OPEN_SLACK_VIEW_URL = "https://slack.com/api/views.open"
