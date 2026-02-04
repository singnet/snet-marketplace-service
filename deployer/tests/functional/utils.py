import json
from typing import Tuple, Union, Any, Optional

from common.constant import RequestPayloadType


def validate_response_ok(response) -> Tuple[int, Union[dict, list]]:
    assert 200 <= response["statusCode"] <= 202, "Response is not OK!"
    body = json.loads(response["body"])
    assert body["status"] == "success", "Response is not successful!"

    return response["statusCode"], body["data"]


def validate_response_bad_request(response) -> Tuple[int, str]:
    assert response["statusCode"] == 400, "Response has no BAD REQUEST error!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"

    return response["statusCode"], body["message"]


def validate_response_server_error(response) -> Union[dict, Any]:
    assert response["statusCode"] == 500, "Response has no INTERNAL SERVER ERROR!"
    body = json.loads(response["body"])
    assert body["status"] == "failed", "Response is suddenly successful!"
    assert body["message"] == "Unexpected server error"

    return body["details"]


def generate_request_event(
    path_parameters: Optional[dict] = None,
    query_parameters: Optional[dict] = None,
    body: Optional[dict] = None,
) -> dict:
    event = {}

    if path_parameters is not None:
        event[RequestPayloadType.PATH_PARAMS] = path_parameters
    if query_parameters is not None:
        event[RequestPayloadType.QUERY_STRING] = query_parameters
    if body is not None:
        event[RequestPayloadType.BODY] = json.dumps(body)

    return event
