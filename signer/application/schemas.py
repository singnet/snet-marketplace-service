import json
from pydantic import BaseModel, ValidationError
from common.constant import RequestPayloadType, PayloadAssertionError
from common.schemas import PayloadValidationError


class GetFreeCallSignatureRequest(BaseModel):
    organization_id: str
    service_id: str
    group_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetFreeCallSignatureRequest":
        try:
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, PayloadAssertionError.MISSING_BODY
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()


class GetSignatureForStateServiceRequest(BaseModel):
    channel_id: int

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForStateServiceRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, PayloadAssertionError.MISSING_BODY
            body = json.loads(event[RequestPayloadType.BODY])
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
            assert event.get(RequestPayloadType.BODY) is not None, PayloadAssertionError.MISSING_BODY
            body = json.loads(event[RequestPayloadType.BODY])
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
            assert event.get(RequestPayloadType.BODY) is not None, PayloadAssertionError.MISSING_BODY
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()
