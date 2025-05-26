import json
from pydantic import BaseModel, ValidationError
from common.schemas import PayloadValidationError

class GetFreeCallSignatureRequest(BaseModel):
    org_id: str
    service_id: str
    group_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetFreeCallSignatureRequest":
        try:
            assert event.get("pathParameters") is not None, "Missing pathParameters"
            assert event.get("body") is not None, "Missing body"

            body = json.loads(event["body"])
            path_parameters = event["pathParameters"]

            data = {**path_parameters, **body}

            return cls.model_validate(data)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetSignatureForStateServiceRequest(BaseModel):
    channel_id: int

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForStateServiceRequest":
        try:
            assert event.get("body") is not None, "Missing body"
            body = json.loads(event["body"])
            return cls.model_validate(body)

        except (ValidationError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetSignatureForRegularCallRequest(BaseModel):
    channel_id: int
    nonce: int
    amount: int

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForRegularCallRequest":
        try:
            assert event.get("body") is not None, "Missing body"
            body = json.loads(event["body"])
            return cls.model_validate(body)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetSignatureForOpenChannelForThirdPartyRequest(BaseModel):
    recipient: str
    group_id: str
    amount_in_cogs: int
    expiration: int
    message_nonce: int
    signer_key: str
    executor_wallet_address: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForOpenChannelForThirdPartyRequest":
        try:
            assert event.get("body") is not None, "Missing body"
            body = json.loads(event["body"])
            return cls.model_validate(body)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetFreeCallTokenRequest(BaseModel):
    org_id: str
    service_id: str
    group_id: str
    public_key: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetFreeCallTokenRequest":
        try:
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"
            data = event["queryStringParameters"]
            return cls.model_validate(data)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetFreecallSignerAddress(BaseModel):
    org_id: str
    service_id: str
    group_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetFreecallSignerAddress":
        try:
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"
            data = event["queryStringParameters"]
            return cls.model_validate(data)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetSignatureForFreeCallFromDaemonRequest(BaseModel):
    org_id: str
    service_id: str
    group_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForFreeCallFromDaemonRequest":
        try:
            assert event.get("queryStringParameters") is not None, "Missing queryStringParameters"
            data = event["queryStringParameters"]
            return cls.model_validate(data)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()