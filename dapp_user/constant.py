from enum import Enum


class SourceDApp(Enum):
    PUBLISHER_DAPP = "PUBLISHER_DAPP"
    MARKETPLACE_DAPP = "MARKETPLACE_DAPP"
    RFAI_DAPP = "RFAI_DAPP"


class CommunicationType(Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"


class PreferenceType(Enum):
    ANNOUNCEMENT = "ANNOUNCEMENT"
