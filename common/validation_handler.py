from functools import wraps
from pydantic import ValidationError

from common.constant import RequestPayloadType, PayloadAssertionError
from common.exceptions import BadRequestException

PAYLOAD_TYPES_ERRORS_RELATIONSHIP = {
    RequestPayloadType.BODY: PayloadAssertionError.MISSING_BODY,
    RequestPayloadType.QUERY_STRING: PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS,
    RequestPayloadType.PATH_PARAMS: PayloadAssertionError.MISSING_PATH_PARAMETERS,
    RequestPayloadType.HEADERS: PayloadAssertionError.MISSING_HEADERS
}


def validation_handler(payload_types: list[RequestPayloadType] = None):
    if payload_types is None:
        payload_types = []
    def decorator(func: callable):
        @wraps(func)
        def wrapper(cls, event: dict, *args, **kwargs):
            try:
                for payload_type in payload_types:
                    assert event.get(payload_type) is not None, (
                        PAYLOAD_TYPES_ERRORS_RELATIONSHIP[payload_type].value
                    )
                return func(cls, event, *args, **kwargs)
            except ValidationError as e:
                missing_params = [x["loc"][0] for x in e.errors()]
                raise BadRequestException(message = f"Missing required parameters: "
                                                    f"{', '.join(missing_params)}")
            except AssertionError as e:
                raise BadRequestException(message = str(e))
            except BadRequestException as e:
                raise e
            except Exception:
                raise BadRequestException(message = "Error while parsing payload")
        return wrapper
    return decorator
