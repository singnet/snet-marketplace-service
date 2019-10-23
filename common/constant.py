COMMON_CNTRCT_PATH = './common/node_modules/singularitynet-platform-contracts'
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/Registry.json'
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + '/abi/MultiPartyEscrow.json'
REG_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/Registry.json'
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + '/networks/MultiPartyEscrow.json'

""" Payment Service """
PAYMENT_METHOD_PAYPAL = "paypal"


class PaymentStatus:
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TransactionStatus:
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class StatusCode:
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500
    CREATED = 201
    OK = 200


class Error:
    UNDEFINED_ERROR_CODE = 0
    CHANNEL_CREATION_FAILED = {"code": UNDEFINED_ERROR_CODE, "message": "CHANNEL_CREATION_FAILED"}
    WALLET_CREATION_FAILED = {"code": UNDEFINED_ERROR_CODE, "message": "WALLET_CREATION_FAILED"}
    FUND_CHANNEL_FAILED = {"code": UNDEFINED_ERROR_CODE, "message": "FUND_CHANNEL_FAILED"}
    PAYMENT_INITIATE_FAILED = {"code": UNDEFINED_ERROR_CODE, "message": "PAYMENT_INITIATE_FAILED"}
    PAYMENT_EXECUTE_FAILED = {"code": UNDEFINED_ERROR_CODE, "message": "PAYMENT_EXECUTE_FAILED"}
    INVALID_ORDER_TYPE = {"code": UNDEFINED_ERROR_CODE, "message": "INVALID_ORDER_TYPE"}
    UNDEFINED_ERROR = {"code": UNDEFINED_ERROR_CODE, "message": "UNDEFINED_ERROR"}
    NO_ERROR = {}


class ResponseStatus:
    FAILED = "failed"
    SUCCESS = "success"
