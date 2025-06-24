import json
from http import HTTPStatus
from typing import List
from unittest.mock import MagicMock

import pytest
from dapp_user.application.handlers import user_handlers
from dapp_user.application.services.user_service import UserService
from dapp_user.domain.models.user_preference import UserPreference as UserPreferenceDomain
from dapp_user.infrastructure.models import User
from dapp_user.infrastructure.repositories import base_repository
from dapp_user.infrastructure.repositories.exceptions import UserNotFoundException
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

    result = user_handlers.get_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert body["data"]["username"] == expected_username


def test_get_user_handler_not_found(
    lambda_event_authorized_not_found: dict,
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
):
    expected_username = lambda_event_authorized_not_found["requestContext"]["authorizer"]["claims"][
        "email"
    ]

    monkeypatch.setattr(base_repository, "default_session", test_session)

    result = user_handlers.get_user_handler(lambda_event_authorized_not_found, context={})

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

    result = user_handlers.add_or_update_user_preference_handler(
        lambda_event_authorized, context={}
    )

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

    result = user_handlers.add_or_update_user_preference_handler(
        lambda_event_authorized, context={}
    )

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

    result = user_handlers.add_or_update_user_preference_handler(
        lambda_event_authorized, context={}
    )

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST
    body = json.loads(result["body"])
    assert body["status"] == "failed"
    assert body["error"]["message"] == "User with username 'integration@example.com' not found"


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

    result = user_handlers.update_user_alerts_handler(lambda_event_authorized, context={})

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

    result = user_handlers.get_user_preferences_handler(lambda_event_authorized, context={})

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

    result = user_handlers.register_user_post_aws_cognito_signup_handler(
        post_confirmation_cognito_event, context={}
    )

    assert result == post_confirmation_cognito_event

    new_user = user_repo.get_user(
        username=post_confirmation_cognito_event["request"]["userAttributes"]["email"]
    )

    assert new_user is not None


def test_delete_user_handler_success(
    lambda_event_authorized: dict,
    create_user_for_deleting: User,
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
    user_repo: UserRepository,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    mock_wallet_api = MagicMock()
    mock_user_service = UserService(wallets_api_client=mock_wallet_api)
    user_handlers.__user_service = mock_user_service

    result = user_handlers.delete_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    deleted_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]
    with pytest.raises(UserNotFoundException):
        user_repo.get_user(deleted_username)


def test_delete_user_handler_failed(
    lambda_event_authorized: dict,
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
    user_repo: UserRepository,
):
    monkeypatch.setattr(base_repository, "default_session", test_session)

    mock_wallet_api = MagicMock()
    mock_user_service = UserService(wallets_api_client=mock_wallet_api)
    user_handlers.__user_service = mock_user_service

    result = user_handlers.delete_user_handler(lambda_event_authorized, context={})

    expected_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST
    body = json.loads(result["body"])
    assert body["status"] == "failed"
    assert body["error"]["message"] == f"User with username '{expected_username}' not found"


def test_create_user_service_review_handler_with_comment(
    lambda_event_authorized: dict,
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    test_session: SessionType,
    user_repo: UserRepository,
):
    expected_user_row_id = 3
    expected_org_id = "test_org_id"
    expected_service_id = "test_service_id"
    expected_user_rating = 3.0
    expected_comment = "test_comment"
    expected_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]

    monkeypatch.setattr(base_repository, "default_session", test_session)

    mock_contract_api = MagicMock()
    mock_user_service = UserService(contract_api_client=mock_contract_api)
    user_handlers.__user_service = mock_user_service

    request_body = {
        "userId": expected_user_row_id,
        "orgId": expected_org_id,
        "serviceId": expected_service_id,
        "user_rating": expected_user_rating,
        "comment": expected_comment,
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = user_handlers.create_user_service_review_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK


    vote = user_repo.get_user_servce_vote(
        expected_user_row_id,
        expected_org_id,
        expected_service_id,
    )
    assert vote is not None
    assert vote.rating == expected_user_rating


    feedback = user_repo.get_user_service_feedback(
        expected_username,
        expected_org_id,
        expected_service_id,
    )
    assert feedback is not None
    assert feedback.comment == expected_comment
