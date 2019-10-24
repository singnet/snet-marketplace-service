class Error:
    UNDEFINED_ERROR_CODE = 0
    CHANNEL_CREATION_FAILED = {
        "code": UNDEFINED_ERROR_CODE,
        "message": "CHANNEL_CREATION_FAILED",
    }
    WALLET_CREATION_FAILED = {
        "code": UNDEFINED_ERROR_CODE,
        "message": "WALLET_CREATION_FAILED",
    }
    FUND_CHANNEL_FAILED = {
        "code": UNDEFINED_ERROR_CODE,
        "message": "FUND_CHANNEL_FAILED",
    }
    PAYMENT_INITIATE_FAILED = {
        "code": UNDEFINED_ERROR_CODE,
        "message": "PAYMENT_INITIATE_FAILED",
    }
    PAYMENT_EXECUTE_FAILED = {
        "code": UNDEFINED_ERROR_CODE,
        "message": "PAYMENT_EXECUTE_FAILED",
    }
    INVALID_ORDER_TYPE = {"code": UNDEFINED_ERROR_CODE, "message": "INVALID_ORDER_TYPE"}
    UNDEFINED_ERROR = {"code": UNDEFINED_ERROR_CODE, "message": "UNDEFINED_ERROR"}
    NO_ERROR = {}
