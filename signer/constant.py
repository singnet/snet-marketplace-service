import os
from signer.settings import settings

NETWORK_ID = settings.network.id
CONTRACT_BASE_PATH = settings.network.networks[NETWORK_ID].contract_base_path
COMMON_CNTRCT_PATH = os.path.abspath(
    os.path.join(f"{CONTRACT_BASE_PATH}/node_modules/singularitynet-platform-contracts")
)
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + "/abi/Registry.json"
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + "/abi/MultiPartyEscrow.json"
REG_ADDR_PATH = COMMON_CNTRCT_PATH + "/networks/Registry.json"
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + "/networks/MultiPartyEscrow.json"
