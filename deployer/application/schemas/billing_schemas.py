import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.application.schemas.queue_schema import QueueEventRequest
from deployer.constant import PeriodType, SortOrder, TypeOfMovementOfFunds
from deployer.exceptions import InvalidPeriodParameter, InvalidOrderParameter, InvalidTypeOfMovementParameter


class CreateOrderRequest(BaseModel):
    amount: int

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "CreateOrderRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)


class SaveEVMTransactionRequest(BaseModel):
    sender: str
    recipient: str
    order_id: str = Field(alias="orderId")
    transaction_hash: str = Field(alias="transactionHash")

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "SaveEVMTransactionRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)


class GetBalanceHistoryRequest(BaseModel):
    limit: int
    page: int
    order: str
    period: str
    type_of_movement: Optional[str] = Field(alias="type", default = None)

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetBalanceHistoryRequest":
        data = event[RequestPayloadType.QUERY_STRING]
        return cls.model_validate(data)

    @field_validator("period")
    @classmethod
    def validate_period(cls, value: str):
        if value not in PeriodType:
            raise InvalidPeriodParameter(actual_value = value)
        return value

    @field_validator("order")
    @classmethod
    def validate_order(cls, value: str):
        if value not in SortOrder:
            raise InvalidOrderParameter()
        return value

    @field_validator("type_of_movement")
    @classmethod
    def validate_type_of_movement(cls, value: Optional[str]):
        if value is not None and value not in TypeOfMovementOfFunds:
            raise InvalidTypeOfMovementParameter()
        return value


class GetMetricsRequest(BaseModel):
    hosted_service_id: str = Field(alias="hostedServiceId")
    period: str

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS, RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetMetricsRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS], **event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)

    @field_validator("period")
    @classmethod
    def validate_period(cls, value: str):
        if value not in PeriodType:
            raise InvalidPeriodParameter(actual_value = value)
        return value

class CallEventConsumerRequest(BaseModel, QueueEventRequest):
    org_id: str = Field(alias="orgId")
    service_id: str | None = Field(alias="serviceId")
    duration: int

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "CallEventConsumerRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)

