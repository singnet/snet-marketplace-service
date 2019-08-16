class StatusCode:
    BAD_PARAMETERS_CODE = 400
    SERVER_ERROR_CODE = 500
    SUCCESS_POST_CODE = 201
    SUCCESS_GET_CODE = 200


HEADER_POST_RESPONSE = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
}


class StatusMessage:
    BAD_PARAMETER = "Request validation failed"
    SERVER_ERROR_MSG = "failed"
    SUCCESS_POST_CODE = "successful"
