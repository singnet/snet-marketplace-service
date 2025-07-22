import json
from http import HTTPStatus
from functools import wraps
from common.constant import ResponseStatus
from common.exceptions import CustomException, FailedResponse
from common.alerts import AlertsProcessor, DefaultProcessor
from common.utils import generate_lambda_response, format_response


def exception_handler(*decorator_args, **decorator_kwargs):
    ENVIRONMENT = decorator_kwargs.get("ENVIRONMENT", "Undefined")
    ALERTS_PROCESSOR = decorator_kwargs.get("ALERTS_PROCESSOR", DefaultProcessor())
    EXCEPTIONS_IGNORING_ALERT = decorator_kwargs.get("EXCEPTIONS_IGNORING_ALERT", ())
    logger = decorator_kwargs["logger"]

    def decorator(handler):

        @wraps(handler)
        def wrapper(*args, **kwargs):

            handler_name = handler.__name__
            event = args[0] if len(args) > 0 else {}
            logger.debug(f"Handler {handler_name} received event: {json.dumps(event)}")

            try:
                return handler(*args, **kwargs)
            except FailedResponse as exc:
                logger.exception(f"Failed response [code {exc.code}]: {exc.message}", exc_info=False)
                response = format_response(ResponseStatus.FAILED, exc.to_dict())
                return generate_lambda_response(exc.http_code, response, cors_enabled=True)
            except Exception as exc:
                logger.exception(f"Exception in lambda handler: {handler_name}", exc_info=True)
                if not isinstance(exc, EXCEPTIONS_IGNORING_ALERT):
                    if isinstance(ALERTS_PROCESSOR, AlertsProcessor):
                        logger.info(f"Sending alert via {ALERTS_PROCESSOR.name}")
                        ALERTS_PROCESSOR.send_handler_event_error(
                            handler_name=handler_name,
                            event=event,
                            error_message=repr(exc),
                            environment=ENVIRONMENT
                        )
                    else:
                        logger.warning("Invalid alerts processor")
                if isinstance(exc, CustomException):
                    http_code = exc.http_code
                    response = exc.to_dict()
                else:
                    http_code = HTTPStatus.INTERNAL_SERVER_ERROR
                    response = {"code": 0, "message": "Unexpected server error", "details": {}}
                response = format_response(ResponseStatus.FAILED, response)
                return generate_lambda_response(http_code, response, cors_enabled=True)

        return wrapper

    return decorator

def worker_exception_handler(*decorator_args, **decorator_kwargs):
    ENVIRONMENT = decorator_kwargs.get("ENVIRONMENT", "Undefined")
    ALERTS_PROCESSOR = decorator_kwargs.get("ALERTS_PROCESSOR", DefaultProcessor())
    EXCEPTIONS_IGNORING_ALERT = decorator_kwargs.get("EXCEPTIONS_IGNORING_ALERT", ())
    logger = decorator_kwargs["logger"]

    def decorator(handler):

        @wraps(handler)
        def wrapper(*args, **kwargs):
            handler_name = handler.__name__
            event = args[0] if len(args) > 0 else {}
            logger.debug(f"Handler {handler_name} received event: {json.dumps(event)}")

            try:
                return handler(*args, **kwargs)
            except Exception as exc:
                logger.exception(f"Exception in cron/trigger lambda handler: {handler_name}", exc_info=True)
                if not isinstance(exc, EXCEPTIONS_IGNORING_ALERT):
                    if isinstance(ALERTS_PROCESSOR, AlertsProcessor):
                        logger.info(f"Sending alert via {ALERTS_PROCESSOR.name}")
                        ALERTS_PROCESSOR.send_handler_event_error(
                            handler_name=handler_name,
                            event=event,
                            error_message=repr(exc),
                            environment=ENVIRONMENT
                        )
                    else:
                        logger.warning("Invalid alerts processor")
                return {}

        return wrapper

    return decorator
