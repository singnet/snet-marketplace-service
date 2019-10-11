COMMON_CNTRCT_PATH = "./common/node_modules/singularitynet-platform-contracts"
REG_CNTRCT_PATH = COMMON_CNTRCT_PATH + "/abi/Registry.json"
MPE_CNTRCT_PATH = COMMON_CNTRCT_PATH + "/abi/MultiPartyEscrow.json"
REG_ADDR_PATH = COMMON_CNTRCT_PATH + "/networks/Registry.json"
MPE_ADDR_PATH = COMMON_CNTRCT_PATH + "/networks/MultiPartyEscrow.json"

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
