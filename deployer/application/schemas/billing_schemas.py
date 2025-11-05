import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.application.schemas.queue_schema import QueueEventRequest
from deployer.config import REQUEST_MAX_LIMIT
from deployer.constant import PeriodType, OrderType, TypeOfMovementOfFunds


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
    limit: int = Field(ge=1, le=REQUEST_MAX_LIMIT, default=REQUEST_MAX_LIMIT)
    page: int = Field(ge=1, default=1)
    order: OrderType = Field(default=OrderType.ASC)
    period: PeriodType = Field(default=PeriodType.ALL)
    type_of_movement: Optional[TypeOfMovementOfFunds] = Field(alias="type", default=None)

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetBalanceHistoryRequest":
        data = event[RequestPayloadType.QUERY_STRING]
        return cls.model_validate(data)


class GetMetricsRequest(BaseModel):
    hosted_service_id: str = Field(alias="hostedServiceId")
    period: PeriodType = Field(default=PeriodType.ALL)

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS, RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetMetricsRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS], **event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)


class CallEventConsumerRequest(BaseModel, QueueEventRequest):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")
    duration: int
    amount: int
    timestamp: datetime

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "CallEventConsumerRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)


class GetBalanceAndRateRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "GetBalanceAndRateRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)
