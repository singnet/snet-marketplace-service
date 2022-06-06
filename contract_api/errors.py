class Error:
    UNDEFINED_ERROR_CODE = 0
    UNDEFINED_ERROR = {"code": UNDEFINED_ERROR_CODE, "message": "UNDEFINED_ERROR"}
    NO_ERROR = {}

    @staticmethod
    def handle_undefined_error(error_message):
        return {"code": 0, "message": error_message}
