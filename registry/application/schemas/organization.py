import json

from common.exceptions import MethodNotImplemented
from registry.settings import settings
from registry.application.schemas.common import PayloadValidationError
from registry.domain.models.organization import Organization as OrganizationEntity
from registry.domain.factory.organization_factory import OrganizationFactory
from registry.exceptions import InvalidOriginException
from registry.constants import ORG_STATUS_LIST, ORG_TYPE_VERIFICATION_TYPE_MAPPING, OrganizationActions, OrganizationType
from infrastructure.storage_provider import StorageProviderType

from pydantic import BaseModel, Field, field_validator, model_validator



class GetGroupByOrganizationIdRequest(BaseModel):
    org_uuid: str

    @classmethod
    def validate_event(cls, event) -> 'GetGroupByOrganizationIdRequest':
        try:
            assert event.get("pathParameters") is not None, "Invalid event path parameters"
            path_parameters = event["pathParameters"]
            assert path_parameters.get("org_uuid") is not None, "Missing organization UUID"
            return cls.model_validate(path_parameters)
        except (AssertionError, json.JSONDecodeError):
            raise PayloadValidationError()


class CreateOrganizationRequest(BaseModel):
    uuid: str
    org_id: str
    name: str
    type: str
    description: str
    short_description: str
    url: str
    duns_no: str
    origin: str
    contacts: dict
    assets: dict
    metadata_uri: str
    groups: list
    addresses: list

    @classmethod
    def validate_event(cls, event: dict) -> 'CreateOrganizationRequest':
        try:
            assert event.get("body") is not None, "Invalid event body"
            body = json.loads(event["body"])
            return cls.model_validate(body)
        except (AssertionError, json.JSONDecodeError):
            raise PayloadValidationError()

    @field_validator("origin")
    @classmethod
    def validate_origin(cls, value):
        if value not in settings.aws.ALLOWED_ORIGIN:
            raise InvalidOriginException()
        return value

    #TODO: Check if it need, maybe we can change payload format
    @model_validator(mode="before")
    @classmethod
    def extract_addresses(cls, data: dict) -> dict:
        if "org_address" in data and "addresses" in data["org_address"]:
            data["addresses"] = data["org_address"]["addresses"]
        return data

    def map_to_entity(self) -> OrganizationEntity:
        return OrganizationEntity(
            uuid=self.uuid,
            org_id=self.org_id,
            name=self.name,
            org_type=self.type,
            description=self.description,
            short_description=self.short_description,
            url=self.url,
            duns_no=self.duns_no,
            origin=self.origin,
            contacts=self.contacts,
            assets=self.assets,
            metadata_uri=self.metadata_uri,
            groups=OrganizationFactory.group_domain_entity_from_group_list_payload(self.groups),
            addresses=OrganizationFactory.domain_address_entity_from_address_list_payload(self.addresses),
            org_state=None,
            members=[]
        )


class UpdateOrganizationRequest(BaseModel):
    uuid: str
    org_id: str
    name: str
    type: str
    description: str
    short_description: str
    url: str
    duns_no: str
    origin: str
    contacts: dict
    assets: dict
    metadata_uri: str
    groups: list
    addresses: list

    action: str

    @field_validator("action")
    @classmethod
    def validate_action(cls, value):
        if value is not None and value not in {
            OrganizationActions.DRAFT.value, 
            OrganizationActions.SUBMIT.value
        }:
            raise ValueError(f"Invalid action: {value}")
        return value

    @classmethod
    def validate_event(cls, event: dict) -> "UpdateOrganizationRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            query_parameters = event.get("queryStringParameters") or {}

            data = {
                **body,
                "action": query_parameters.get("action")
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()

    def map_to_entity(self) -> OrganizationEntity:
        return OrganizationEntity(
            uuid=self.uuid,
            org_id=self.org_id,
            name=self.name,
            org_type=self.type,
            description=self.description,
            short_description=self.short_description,
            url=self.url,
            duns_no=self.duns_no,
            origin=self.origin,
            contacts=self.contacts,
            assets=self.assets,
            metadata_uri=self.metadata_uri,
            groups=OrganizationFactory.group_domain_entity_from_group_list_payload(self.groups),
            addresses=OrganizationFactory.domain_address_entity_from_address_list_payload(self.addresses),
            org_state=None,
            members=[]
        )


class PublishOrganizationRequest(BaseModel):
    org_uuid: str
    storage_provider: StorageProviderType
    lighthouse_token: None | str = None

    @classmethod
    def validate_event(cls, event: dict) -> "PublishOrganizationRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {
                **body,
                "org_uuid": path_parameters["org_uuid"],
                "provider_storage": path_parameters["provider_storage"]
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class SaveTransactionHashForOrganizationRequest(BaseModel):
    org_uuid: str
    transaction_hash: str
    wallet_address: str
    nonce: str

    @classmethod
    def validate_event(cls, event: dict) -> "SaveTransactionHashForOrganizationRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class GetAllMembersRequest(BaseModel):
    org_uuid: str
    status: str
    role: str
   
    @classmethod
    def validate_event(cls, event: dict) -> "GetAllMembersRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"

            query_string_parameters = event["queryStringParameters"]
            path_parameters = event["pathPerameters"]

            data = {
                **path_parameters,
                **query_string_parameters
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()

       
class GetMemberRequest(BaseModel):
    org_uuid: str
    member_username: str = Field(alias="username")

    @classmethod
    def validate_event(cls, event: dict) -> "GetMemberRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            return cls.model_validate(event["pathPerameters"])

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class InviteMembersRequest(BaseModel):
    org_uuid: str
    members: list

    @classmethod
    def validate_event(cls, event: dict) -> "InviteMembersRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class VerifyCodeRequest(BaseModel):
    invite_code: str

    @classmethod
    def validate_event(cls, event: dict) -> "VerifyCodeRequest":
        try:
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"
            return cls.model_validate(event["queryStringPerameters"])

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class PublishMembersRequest(BaseModel):
    org_uuid: str
    transaction_hash: str
    members: list

    @classmethod
    def validate_event(cls, event: dict) -> "PublishMembersRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class DeleteMembersRequest(BaseModel):
    org_uuid: str
    members: list

    @classmethod
    def validate_event(cls, event: dict) -> "DeleteMembersRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class RegisterMemberRequest(BaseModel):
    org_uuid: str
    invite_code: str
    wallet_address: str

    @classmethod
    def validate_event(cls, event: dict) -> "RegisterMemberRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {
                **body,
                **path_parameters,
            }

            return cls.model_validate(data)

        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


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
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"
            return cls.model_validate(event["queryStringParameters"])
        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()


class VerifyOrgIdRequest(BaseModel):
    org_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "VerifyOrgIdRequest":
        try:
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"
            return cls.model_validate(event["queryStringParameters"])
        except (AssertionError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()