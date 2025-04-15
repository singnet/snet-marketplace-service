import os
from enum import Enum
from wallets.config import CONTRACT_BASE_PATH

COMMON_CNTRCT_PATH = os.path.abspath(os.path.join(f"{CONTRACT_BASE_PATH}/node_modules/singularitynet-platform-contracts"))
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/Registry.json'
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/MultiPartyEscrow.json'
REG_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/Registry.json'
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/MultiPartyEscrow.json'
GENERAL_WALLET_TYPE = "GENERAL"
REQUIRED_KEYS_FOR_LAMBDA_EVENT = ['path', 'httpMethod']


class WalletStatus(Enum):
    ACTIVE = 0
    INACTIVE = 1
