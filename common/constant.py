COMMON_CNTRCT_PATH = './common/node_modules/singularitynet-platform-contracts'
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/Registry.json'
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/MultiPartyEscrow.json'
REG_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/Registry.json'
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/MultiPartyEscrow.json'
STATUS_CODE_SUCCESS = 200
STATUS_CODE_REDIRECT = 301
STATUS_CODE_FAILED = 500


class StatusCode:
    BAD_PARAMETERS_CODE = 400
    SERVER_ERROR_CODE = 500
    SUCCESS_POST_CODE = 201
    SUCCESS_GET_CODE = 200


HEADER_POST_RESPONSE = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST"
}