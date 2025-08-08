import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.constant import DaemonStorageType
from deployer.exceptions import InvalidDaemonStorageTypeParameter


class InitiateOrderRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")
    service_endpoint: str = Field(alias="serviceEndpoint")
    daemon_storage_type: str = Field(alias="storageType")
    parameters: Optional[dict] = {}

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "InitiateOrderRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)

    @field_validator("storage_type")
    @classmethod
    def validate_storage_type(cls, value: str):
        if value not in DaemonStorageType:
            raise InvalidDaemonStorageTypeParameter()


class GetOrderRequest(BaseModel):
    order_id: str = Field(alias="orderId")

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "GetOrderRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)

