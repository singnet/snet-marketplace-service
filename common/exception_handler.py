import sys
import traceback

from common.constant import StatusCode
from common.utils import Utils, generate_lambda_response


def exception_handler(*decorator_args, **decorator_kwargs):
    logger = decorator_kwargs["logger"]
    NETWORK_ID = decorator_kwargs.get("NETWORK_ID", None)
    SLACK_HOOK = decorator_kwargs.get("SLACK_HOOK", None)
    EXCEPTIONS = decorator_kwargs.get("EXCEPTIONS", ())

    def decorator(func):
        def wrapper(*args, **kwargs):
            handler_name = decorator_kwargs.get("handler_name", func.__name__)
            path = kwargs.get("event", {}).get("path", None)
            path_parameters = kwargs.get("event", {}).get("pathParameters", {})
            query_string_parameters = kwargs.get("event", {}).get("queryStringParameters", {})
            body = kwargs.get("event", {}).get("body", "{}")

            error_message = f"Error Reported! \n" \
                            f"network_id: {NETWORK_ID}\n" \
                            f"path: {path}, \n" \
                            f"handler: {handler_name} \n" \
                            f"pathParameters: {path_parameters} \n" \
                            f"queryStringParameters: {query_string_parameters} \n" \
                            f"body: {body} \n" \
                            f"x-ray-trace-id: None \n" \
                            f"error_description: \n"

            try:
                return func(*args, **kwargs)
            except EXCEPTIONS as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                exc_tb_lines = traceback.format_tb(exc_tb)
                error_message = error_message + e.error_message + "\n"
                logger.exception(error_message)

                slack_message = error_message
                for exc_lines in exc_tb_lines:
                    slack_message = slack_message + exc_lines
                slack_message = f"```{slack_message}```"
                Utils().report_slack(type=0, slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)

                return generate_lambda_response(
                    StatusCode.INTERNAL_SERVER_ERROR,
                    {
                        "status": "failed",
                        "data": "",
                        "error": {
                            "message": e.error_message,
                            "details": e.error_details
                        }
                    },
                    cors_enabled=True
                )
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                exc_tb_lines = traceback.format_tb(exc_tb)
                logger.exception(error_message)

                slack_message = error_message
                for exc_lines in exc_tb_lines:
                    slack_message = slack_message + exc_lines
                slack_message = f"```{slack_message}```"
                Utils().report_slack(type=0, slack_msg=slack_message, SLACK_HOOK=SLACK_HOOK)

                return generate_lambda_response(
                    StatusCode.INTERNAL_SERVER_ERROR,
                    {
                        "status": "failed",
                        "data": "",
                        "error": {
                            "code": 0,
                            "message": repr(e),
                            "details": {}
                        }
                    },
                    cors_enabled=True
                )

        return wrapper

    return decorator
