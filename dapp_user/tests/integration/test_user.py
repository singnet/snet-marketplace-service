import json
from http import HTTPStatus

from dapp_user.application.handlers.user_handlers import get_user_handler
from dapp_user.infrastructure.repositories import base_repository


def test_get_user_handler_returns_specific_user(
    lambda_event_authorized,
    create_test_users,
    monkeypatch,
    test_session,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = get_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert (
        body["data"]["username"]
        == lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]
    )


def test_get_user_handler_not_found(
    lambda_event_authorized,
    monkeypatch,
    test_session,
):
    username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]

    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = get_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST

    body = json.loads(result["body"])
    assert body["status"] == "failed"
    assert body["error"]["message"] == f"User with username '{username}' not found"
