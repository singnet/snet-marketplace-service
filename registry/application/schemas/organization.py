import json

from pydantic import ValidationError

from common.exceptions import MethodNotImplemented, BadRequestException
from registry.settings import settings
from common.constant import RequestPayloadType, PayloadAssertionError
from registry.exceptions import InvalidOriginException
from registry.constants import (
    ORG_STATUS_LIST,
    ORG_TYPE_VERIFICATION_TYPE_MAPPING,
    OrganizationActions,
    OrganizationType,
)
from registry.infrastructure.storage_provider import StorageProviderType

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class GetGroupByOrganizationIdRequest(BaseModel):
    org_uuid: str

    @classmethod
    def validate_event(cls, event) -> "GetGroupByOrganizationIdRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            path_parameters = event[RequestPayloadType.PATH_PARAMS]
            assert path_parameters.get("org_uuid") is not None, "Missing organization UUID"
            return cls.model_validate(path_parameters)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class CreateOrganizationRequest(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    uuid: str = Field(alias="org_uuid")
    id: str = Field(alias="org_id")
    name: str = Field(alias="org_name")
    type: str = Field(alias="org_type")
    description: str
    short_description: str
    url: str
    duns_no: str
    origin: str
    contacts: list
    assets: dict
    metadata_uri: str
    groups: list
    org_address: dict

    @classmethod
    def validate_event(cls, event: dict) -> "CreateOrganizationRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

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

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, value):
        if value not in settings.aws.ALLOWED_ORIGIN:
            raise InvalidOriginException()
        return value

    # TODO: Check if it need, maybe we can change payload format
    @model_validator(mode="before")
    @classmethod
    def extract_addresses(cls, data: dict) -> dict:
        if "org_address" in data and "addresses" in data["org_address"]:
            data["addresses"] = data["org_address"]["addresses"]
        return data


class UpdateOrganizationRequest(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    uuid: str = Field(alias="org_uuid")
    id: str = Field(alias="org_id")
    name: str = Field(alias="org_name")
    type: str = Field(alias="org_type")
    description: str
    short_description: str
    url: str
    duns_no: str
    origin: str
    contacts: list
    assets: dict
    metadata_uri: str
    groups: list
    org_address: dict

    action: str

    @field_validator("action")
    @classmethod
    def validate_action(cls, value):
        if value is not None and value not in {
            OrganizationActions.DRAFT.value,
            OrganizationActions.SUBMIT.value,
        }:
            raise ValueError(f"Invalid action: {value}")
        return value

    @classmethod
    def validate_event(cls, event: dict) -> "UpdateOrganizationRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            query_parameters = event.get(RequestPayloadType.QUERY_STRING) or {}
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, "action": query_parameters.get("action"), **path_parameters}

            return cls.model_validate(data)

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


class PublishOrganizationRequest(BaseModel):
    org_uuid: str
    storage_provider: StorageProviderType = StorageProviderType.IPFS
    lighthouse_token: None | str = None

    @classmethod
    def validate_event(cls, event: dict) -> "PublishOrganizationRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**path_parameters, **body}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class SaveTransactionHashForOrganizationRequest(BaseModel):
    org_uuid: str
    transaction_hash: str
    wallet_address: str
    nonce: int | None = None

    @classmethod
    def validate_event(cls, event: dict) -> "SaveTransactionHashForOrganizationRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class GetAllMembersRequest(BaseModel):
    org_uuid: str
    status: str | None = None
    role: str | None = None

    @classmethod
    def validate_event(cls, event: dict) -> "GetAllMembersRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, (
                PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS.value)

            query_string_parameters = event[RequestPayloadType.QUERY_STRING]
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**path_parameters, **query_string_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class GetMemberRequest(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    org_uuid: str
    member_username: str = Field(alias="username")

    @classmethod
    def validate_event(cls, event: dict) -> "GetMemberRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            return cls.model_validate(event[RequestPayloadType.PATH_PARAMS])

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class InviteMembersRequest(BaseModel):
    org_uuid: str
    members: list

    @classmethod
    def validate_event(cls, event: dict) -> "InviteMembersRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class VerifyCodeRequest(BaseModel):
    invite_code: str

    @classmethod
    def validate_event(cls, event: dict) -> "VerifyCodeRequest":
        try:
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, (
                PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS.value)
            return cls.model_validate(event[RequestPayloadType.QUERY_STRING])

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class PublishMembersRequest(BaseModel):
    org_uuid: str
    transaction_hash: str
    members: list

    @classmethod
    def validate_event(cls, event: dict) -> "PublishMembersRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class DeleteMembersRequest(BaseModel):
    org_uuid: str
    members: list

    @classmethod
    def validate_event(cls, event: dict) -> "DeleteMembersRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class RegisterMemberRequest(BaseModel):
    invite_code: str
    wallet_address: str

    @classmethod
    def validate_event(cls, event: dict) -> "RegisterMemberRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)
            body = json.loads(event[RequestPayloadType.BODY])

            return cls.model_validate(body)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class VerifyOrgRequest(BaseModel):
    verification_type: str
    status: str
    updated_by: str
    username: str | None = None
    org_uuid: str | None = None
    comment: str | None = None
    org_type: str | None = None

    @field_validator("verification_type")
    @classmethod
    def validate_verification_type(cls, v):
        if v not in ORG_TYPE_VERIFICATION_TYPE_MAPPING:
            raise MethodNotImplemented()
        return v

    @model_validator(mode="after")
    def check_status_and_assign_org_type(self) -> "VerifyOrgRequest":
        org_type = ORG_TYPE_VERIFICATION_TYPE_MAPPING[self.verification_type]
        self.org_type = org_type

        if org_type == OrganizationType.ORGANIZATION.value:
            if self.status not in ORG_STATUS_LIST:
                raise MethodNotImplemented()

        return self

    @classmethod
    def validate_event(cls, event: dict) -> "VerifyOrgRequest":
        try:
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, (
                PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS.value)
            return cls.model_validate(event[RequestPayloadType.QUERY_STRING])
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


class VerifyOrgIdRequest(BaseModel):
    org_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "VerifyOrgIdRequest":
        try:
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, (
                PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS.value)
            return cls.model_validate(event[RequestPayloadType.QUERY_STRING])

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")
