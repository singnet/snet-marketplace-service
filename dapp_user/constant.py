from enum import Enum


class SourceDApp(str, Enum):
    PUBLISHER_DAPP = "PUBLISHER_DAPP"
    MARKETPLACE_DAPP = "MARKETPLACE_DAPP"
    RFAI_DAPP = "RFAI_DAPP"
    TOKEN_STAKE_DAPP = "TOKEN_STAKE_DAPP"


class CommunicationType(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class PreferenceType(str, Enum):
    FEATURE_RELEASE = "FEATURE_RELEASE"
    WEEKLY_SUMMARY = "WEEKLY_SUMMARY"
    COMMENTS_AND_MESSAGES = "COMMENTS_AND_MESSAGES"
    TOKEN_STAKE_NOTIFICATION = "TOKEN_STAKE_NOTIFICATION"


class Status(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class CognitoTriggerSource(str, Enum):
    POST_CONFIRMATION = "PostConfirmation_ConfirmSignUp"
