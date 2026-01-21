from enum import Enum

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


class BuildStatus:
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class TransactionStatus:
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PROCESSING = "PROCESSING"
    NOT_SUBMITTED = "NOT_SUBMITTED"


class StatusCode:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    INTERNAL_SERVER_ERROR = 500
    CREATED = 201
    ACCEPTED = 202
    OK = 200
    FOUND = 302


class StatusDescription:
    BAD_REQUEST = "Bad Request"


class ErrorDescription:
    METHOD_NOT_ALLOWED = "Method Not Allowed"
    NOT_FOUND = "Not Found"


class ResponseStatus:
    FAILED = "failed"
    SUCCESS = "success"


COGS_TO_AGI = "0.00000001"


class TokenSymbol(Enum):
    AGIX = "AGIX"
    NTX = "NTX"
    RJV = "RJV"
    CGV = "CGV"
    FET = "FET"


class ProviderType(Enum):
    http = "HTTP_PROVIDER"
    ws = "WS_PROVIDER"


class RequestPayloadType(str, Enum):
    BODY = "body"
    PATH_PARAMS = "pathParameters"
    QUERY_STRING = "queryStringParameters"
    HEADERS = "headers"


class PayloadAssertionError(str, Enum):
    MISSING_PATH_PARAMETERS = "Missing pathParameters"
    MISSING_QUERY_STRING_PARAMETERS = "Missing queryStringParameters"
    MISSING_BODY = "Missing body"
    MISSING_HEADERS = "Missing headers"