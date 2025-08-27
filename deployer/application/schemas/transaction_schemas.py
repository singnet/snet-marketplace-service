import json
from typing import Optional

from pydantic import Field, BaseModel

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler


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


class GetTransactionsRequest(BaseModel):
    order_id: Optional[str] = Field(alias="orderId", default=None)
    transaction_hash: Optional[str] = Field(alias="transactionHash", default=None)
    daemon_id: Optional[str] = Field(alias="daemonId", default=None)

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetTransactionsRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)
