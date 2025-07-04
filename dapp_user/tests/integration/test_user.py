import json
from http import HTTPStatus
from typing import List, Tuple
from unittest.mock import MagicMock

import pytest
from dapp_user.application.handlers import user_handlers
from dapp_user.application.services.user_service import UserService
from dapp_user.domain.interfaces.user_identity_manager_interface import UserIdentityManager
from dapp_user.domain.models.user_preference import UserPreference as UserPreferenceDomain
from dapp_user.domain.models.user_service_feedback import (
    UserServiceFeedback as UserServiceFeedbackDomain,
)
from dapp_user.domain.models.user_service_vote import UserServiceVote as UserServiceVoteDomain
from dapp_user.infrastructure.db import session_scope
from dapp_user.infrastructure.models import User
from dapp_user.infrastructure.repositories.exceptions import UserNotFoundException
from dapp_user.infrastructure.repositories.user_repository import UserRepository
from dapp_user.tests.integration.conftest import TEST_USER
from pytest import MonkeyPatch
from sqlalchemy.orm import sessionmaker


def test_get_user_handler_returns_specific_user(
    lambda_event_authorized: dict,
    create_test_users: List,
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

    result = user_handlers.get_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK
    body = json.loads(result["body"])
    assert body["status"] == "success"
    assert (
        body["data"]["username"]
        == lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]
    )


def test_get_user_handler_not_found(
    lambda_event_authorized_not_found: dict,
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

    expected_username = lambda_event_authorized_not_found["requestContext"]["authorizer"]["claims"][
        "email"
    ]

    result = user_handlers.get_user_handler(lambda_event_authorized_not_found, context={})

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST

    body = json.loads(result["body"])
    assert body["status"] == "failed"
    assert body["error"]["message"] == f"User with username '{expected_username}' not found"


def test_add_or_update_user_preference_handler(
    lambda_event_authorized: dict,
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

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
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

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
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

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
    assert body["error"]["message"] == f"User with username '{TEST_USER}' not found"


def test_update_user_alerts_handler(
    lambda_event_authorized: dict,
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

    request_body = {
        "emailAlerts": True,
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = user_handlers.update_user_alerts_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    body = json.loads(result["body"])
    assert body["status"] == "success"

    with session_scope(test_session_factory) as session:
        user = UserRepository().get_user(
            session=session,
            username=lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"],
        )
        assert user.email_alerts is True


def test_get_user_preferences_handler(
    lambda_event_authorized: dict,
    create_test_user_preferences: List[UserPreferenceDomain],
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

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
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

    result = user_handlers.post_aws_cognito_signup_handler(
        post_confirmation_cognito_event, context={}
    )

    assert result == post_confirmation_cognito_event

    with session_scope(test_session_factory) as session:
        new_user = UserRepository().get_user(
            session=session,
            username=post_confirmation_cognito_event["request"]["userAttributes"]["email"],
        )

    assert new_user is not None


def test_delete_user_handler_success(
    lambda_event_authorized: dict,
    create_user_for_deleting: User,
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    mock_wallet_api = MagicMock()

    monkeypatch.setattr(
        user_handlers,
        "__user_service",
        UserService(wallets_api_client=mock_wallet_api, session_factory=test_session_factory),
    )

    result = user_handlers.delete_user_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    deleted_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]
    with pytest.raises(UserNotFoundException):
        with session_scope(test_session_factory) as session:
            UserRepository().get_user(session, deleted_username)


def test_delete_user_handler_failed(
    lambda_event_authorized: dict,
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    mock_wallet_api = MagicMock()

    monkeypatch.setattr(
        user_handlers,
        "__user_service",
        UserService(wallets_api_client=mock_wallet_api, session_factory=test_session_factory),
    )
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
    test_session_factory: sessionmaker,
):
    mock_contract_api = MagicMock()

    monkeypatch.setattr(
        user_handlers,
        "__user_service",
        UserService(contract_api_client=mock_contract_api, session_factory=test_session_factory),
    )
    expected_user_row_id = 3
    expected_org_id = "test_org_id"
    expected_service_id = "test_service_id"
    expected_user_rating = 3.0
    expected_comment = "test_comment"
    expected_username = lambda_event_authorized["requestContext"]["authorizer"]["claims"]["email"]

    request_body = {
        "orgId": expected_org_id,
        "serviceId": expected_service_id,
        "user_rating": expected_user_rating,
        "comment": expected_comment,
    }

    lambda_event_authorized["body"] = json.dumps(request_body)

    result = user_handlers.create_user_review_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK

    with session_scope(test_session_factory) as session:
        vote = UserRepository().get_user_service_vote(
            session,
            expected_user_row_id,
            expected_org_id,
            expected_service_id,
        )
        assert vote is not None
        assert vote.rating == expected_user_rating

        feedback = UserRepository().get_user_service_feedback(
            session,
            expected_username,
            expected_org_id,
            expected_service_id,
        )
        assert feedback is not None
        assert feedback.comment == expected_comment


def test_get_user_review(
    lambda_event_authorized: dict,
    create_test_user_feedback_vote: Tuple[UserServiceVoteDomain, UserServiceFeedbackDomain],
    monkeypatch: MonkeyPatch,
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )

    request_params = {"org_id": "test_org", "service_id": "test_service"}

    lambda_event_authorized["queryStringParameters"] = request_params

    result = user_handlers.get_user_service_review_handler(lambda_event_authorized, context={})

    assert result["statusCode"] == HTTPStatus.OK
    body = json.loads(result["body"])
    assert body["data"]["rating"] == 5.0
    assert body["data"]["comment"] == "test"


def test_sync_users_handler(
    create_test_users: List[User],
    monkeypatch: MonkeyPatch,
    mock_user_identity_manager: UserIdentityManager,
    fake_cognito_users: List[User],
    test_session_factory: sessionmaker,
):
    monkeypatch.setattr(
        user_handlers, "__user_service", UserService(session_factory=test_session_factory)
    )
    mock_user_service = UserService(user_identity_manager=mock_user_identity_manager)
    user_handlers.__user_service = mock_user_service

    user_handlers.sync_users_handler(event={}, context={})

    with session_scope(test_session_factory) as session:
        for cognito_user in fake_cognito_users:
            user = UserRepository().get_user(session=session,username=cognito_user.username)
            assert cognito_user.account_id == user.account_id
