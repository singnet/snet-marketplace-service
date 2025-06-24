import json
from typing import List

from common.constant import PayloadAssertionError, RequestPayloadType
from common.exceptions import BadRequestException
from dapp_user.constant import (
    CommunicationType,
    PreferenceType,
    SourceDApp,
    Status,
)
from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AddOrUpdateUserPreferenceRequest(BaseModel):
    communication_type: CommunicationType
    preference_type: PreferenceType
    source: SourceDApp
    status: Status
    opt_out_reason: str | None = None


class AddOrUpdateUserPreferencesRequest(BaseModel):
    user_preferences: List[AddOrUpdateUserPreferenceRequest]

    @classmethod
    def validate_event(cls, event: dict) -> "AddOrUpdateUserPreferencesRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(
                message=f"Missing required parameters: {', '.join(str(p) for p in missing_params)}"
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


class DeleteUserRequest(BaseModel):
    username: str | None = None

    @classmethod
    def validate_event(cls, event: dict) -> "DeleteUserRequest":
        try:
            data = event.get(RequestPayloadType.QUERY_STRING)
            return cls.model_validate(data if data else {})
        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(
                message=f"Missing required parameters: {', '.join(str(p) for p in missing_params)}"
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


class CognitoUserAttributes(BaseModel):
    sub: str
    email: str
    email_verified: bool


class CognitoRequest(BaseModel):
    user_attributes: CognitoUserAttributes = Field(..., alias="userAttributes")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CognitoCallerContext(BaseModel):
    aws_sdk_version: str = Field(..., alias="awsSdkVersion")
    client_id: str = Field(..., alias="clientId")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CognitoUserPoolEvent(BaseModel):
    version: str
    trigger_source: str = Field(..., alias="triggerSource")
    region: str
    user_pool_id: str = Field(..., alias="userPoolId")
    name: str = Field(..., alias="userName")
    caller_context: CognitoCallerContext = Field(..., alias="callerContext")
    request: CognitoRequest

    model_config = ConfigDict(
        populate_by_name=True,
    )


class UpdateUserAlertRequest(BaseModel):
    email_alerts: bool = Field(..., alias="emailAlerts")
    is_terms_accepted: bool = Field(..., alias="isTermsAccepted")

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @classmethod
    def validate_event(cls, event: dict) -> "UpdateUserAlertRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(
                message=f"Missing required parameters: {', '.join(str(p) for p in missing_params)}"
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


class GetUserFeedbackRequest(BaseModel):
    org_id: str = Field(..., alias="orgId")
    service_id: str = Field(..., alias="serviceId")

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @classmethod
    def validate_event(cls, event: dict) -> "GetUserFeedbackRequest":
        try:
            data = event.get(RequestPayloadType.PATH_PARAMS)
            return cls.model_validate(data)
        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(
                message=f"Missing required parameters: {', '.join(str(p) for p in missing_params)}"
            )
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


class CreateUserServiceReviewRequest(BaseModel):
    user_row_id: int = Field(..., alias="userId")
    org_id: str = Field(..., alias="orgId")
    service_id: str = Field(..., alias="serviceId")
    user_rating: float = Field(..., alias="userRating")
    comment: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @classmethod
    def validate_event(cls, event: dict) -> "CreateUserServiceReviewRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(
                message=f"Missing required parameters: {', '.join(str(p) for p in missing_params)}"
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")
