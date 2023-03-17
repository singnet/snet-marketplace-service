from enum import Enum


class EventType(Enum):
    REGISTRY = "REGISTRY"
    MPE = "MPE"
    RFAI = "RFAI"
    TOKEN_STAKE = "TOKEN_STAKE"
    SINGULARITYNET_AIRDROP = 'SINGULARITYNET_AIRDROP'
    OCCAM_SNET_AIRDROP = 'OCCAM_SNET_AIRDROP'
    CONVERTER_AGIX = 'CONVERTER_AGIX'
    CONVERTER_NTX = 'CONVERTER_NTX'
    CONVERTER_RJV = 'CONVERTER_RJV'


class NodeModulesPackagePath(Enum):
    BRIDGE = "node_modules/singularitynet-bridge"
