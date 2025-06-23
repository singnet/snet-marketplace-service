import json
from http import HTTPStatus
from typing import List

from dapp_user.application.handlers.user_handlers import (
    add_or_update_user_preference_handler,
    get_user_handler,
    get_user_preferences_handler,
    register_user_post_aws_cognito_signup_handler,
    update_user_alerts_handler,
)
from dapp_user.domain.models.user_preference import UserPreference as UserPreferenceDomain
from dapp_user.infrastructure.models import User
from dapp_user.infrastructure.repositories import base_repository
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from pytest import MonkeyPatch
from sqlalchemy.orm import Session as SessionType


def test_get_user_handler_returns_specific_user(
    lambda_event_authorized: dict,
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    expected_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]
    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = get_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert body["data"]["username"] == expected_username


def test_get_user_handler_not_found(
    lambda_event_authorized: dict,
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    expected_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]

    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = get_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST

    body = json.loads(result["body"])
    assert body["status"] == "failed"
    assert body["error"]["message"] == f"User with username '{expected_username}' not found"


def test_add_or_update_user_preference_handler(
    lambda_event_authorized: dict,
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    request_body = {
        "user_preferences": [
            {
                "communication_type": "EMAIL",
                "preference_type": "FEATURE_RELEASE",
                "source": "MARKETPLACE_DAPP",
                "status": "ENABLED",
            }
        ]
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = add_or_update_user_preference_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert body["data"] == ["ENABLED"]


def test_add_or_update_user_preference_handler_disable(
    lambda_event_authorized: dict,
    create_test_user_preferences: List[UserPreferenceDomain],
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    request_body = {
        "user_preferences": [
            {
                "communication_type": "EMAIL",
                "preference_type": "FEATURE_RELEASE",
                "source": "MARKETPLACE_DAPP",
                "status": "DISABLED",
                "opt_out_reason": "No longer interested",
            }
        ]
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = add_or_update_user_preference_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert body["data"] == ["DISABLED"]


def test_add_or_update_user_preference_handler_not_found(
    lambda_event_authorized: dict,
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    request_body = {
        "user_preferences": [
            {
                "communication_type": "EMAIL",
                "preference_type": "FEATURE_RELEASE",
                "source": "MARKETPLACE_DAPP",
                "status": "DISABLED",
            }
        ]
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = add_or_update_user_preference_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST
    body = json.loads(result["body"])
    assert body["status"] == "failed"
    assert body["error"]["message"] == "User with username 'integrationuser' not found"


def test_update_user_alerts_handler(
    lambda_event_authorized: dict,
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
    user_repo: UserRepository,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    request_body = {
        "email_alerts": True,
        "is_terms_accepted": True,
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = update_user_alerts_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"

    user = user_repo.get_user(
        username=lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]
    )
    assert user.email_alerts is True
    assert user.is_terms_accepted is True


def test_get_user_preferences_handler(
    lambda_event_authorized: dict,
    create_test_user_preferences: List[UserPreferenceDomain],
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = get_user_preferences_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK
    body = json.loads(result["body"])
    user_preferences: List[dict] = body["data"]

    assert len(user_preferences) == len(create_test_user_preferences)

    for actual, expected in zip(user_preferences, create_test_user_preferences):
        assert actual == expected.to_dict()


def test_register_user_post_aws_cognito_signup_handler(
    post_confirmation_cognito_event: dict,
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
    user_repo: UserRepository,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = register_user_post_aws_cognito_signup_handler(
        post_confirmation_cognito_event, context={}
    )

    assert result == post_confirmation_cognito_event

    new_user = user_repo.get_user(
        username=post_confirmation_cognito_event["request"]["userAttributes"]["email"]
    )

    assert new_user is not None
