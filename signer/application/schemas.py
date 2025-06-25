import json

from common.constant import PayloadAssertionError, RequestPayloadType
from common.exceptions import BadRequestException
from pydantic import BaseModel, ValidationError


class GetFreeCallSignatureRequest(BaseModel):
    organization_id: str
    service_id: str
    group_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetFreeCallSignatureRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            formatted_errors = [
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"]
                } for err in e.errors()
            ]
            raise BadRequestException(
                message="Validation failed for request body.",
                details={"validation_erros": formatted_errors}
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


class GetSignatureForStateServiceRequest(BaseModel):
    channel_id: int

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForStateServiceRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            formatted_errors = [
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"]
                } for err in e.errors()
            ]
            raise BadRequestException(
                message="Validation failed for request body.",
                details={"validation_erros": formatted_errors}
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


class GetSignatureForRegularCallRequest(BaseModel):
    channel_id: int
    nonce: int
    amount: int

    @classmethod
    def validate_event(cls, event: dict) -> "GetSignatureForRegularCallRequest":
        try:
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            formatted_errors = [
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"]
                } for err in e.errors()
            ]
            raise BadRequestException(
                message="Validation failed for request body.",
                details={"validation_erros": formatted_errors}
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")


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
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY
            )
            body = json.loads(event[RequestPayloadType.BODY])
            return cls.model_validate(body)

        except ValidationError as e:
            formatted_errors = [
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"]
                } for err in e.errors()
            ]
            raise BadRequestException(
                message="Validation failed for request body.",
                details={"validation_erros": formatted_errors}
            )
        except AssertionError as e:
            raise BadRequestException(message=str(e))
        except Exception:
            raise BadRequestException(message="Error while parsing payload")
