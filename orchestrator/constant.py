from enum import Enum

REQUIRED_KEYS_FOR_LAMBDA_EVENT = ["path", "httpMethod"]


class OrganizationType(Enum):
    ORGANIZATION = "organization"
    INDIVIDUAL = "individual"


class VerificationType(Enum):
    DUNS = "DUNS"
    JUMIO = "JUMIO"
