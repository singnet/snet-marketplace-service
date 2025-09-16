from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    pass


class SaveEVMTransactionRequest(BaseModel):
    pass


class GetBalanceRequest(BaseModel):
    pass


class GetBalanceHistoryRequest(BaseModel):
    pass


class GetMetricsRequest(BaseModel):
    pass


class UpdateTransactionStatusRequest(BaseModel):
    pass


class CallEventConsumerRequest(BaseModel):
    pass

