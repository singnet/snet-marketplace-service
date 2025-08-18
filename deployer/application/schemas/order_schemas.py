import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.constant import AUTH_PARAMETERS
from deployer.exceptions import InvalidServiceAuthParameters


class InitiateOrderRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")
    service_endpoint: str = Field(alias="serviceEndpoint")
    auth_parameters: Optional[dict] = Field(alias="authParameters", default=None)

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "InitiateOrderRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)

    @field_validator("auth_parameters")
    @classmethod
    def validate_auth_parameters(cls, value: Optional[dict]):
        if value is not None: # auth parameters are optional
            for param in AUTH_PARAMETERS:
                if param not in value.keys():
                    raise InvalidServiceAuthParameters()


class GetOrderRequest(BaseModel):
    order_id: str = Field(alias="orderId")

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "GetOrderRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)

