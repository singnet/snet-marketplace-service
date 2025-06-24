from pydantic import BaseModel, model_validator, Field

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from contract_api.exceptions import InvalidUpdatingChannelParameters


class GetChannelsRequest(BaseModel):
    wallet_address: str = Field(alias="walletAddress")

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetChannelsRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)


class GetGroupChannelsRequest(BaseModel):
    user_address: str
    org_id: str
    group_id: str

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetGroupChannelsRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)


class UpdateConsumedBalanceRequest(BaseModel):
    channel_id: int = Field(alias="channelId")
    signed_amount: int | None = Field(alias="signedAmount", default = None)
    org_id: str | None = Field(alias="orgId", default = None)
    service_id: str | None = Field(alias="serviceId", default = None)

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS, RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "UpdateConsumedBalanceRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS], **event[RequestPayloadType.BODY]}
        return cls.model_validate(data)

    @model_validator(mode="after")
    def validate_body_parameters(self) -> "UpdateConsumedBalanceRequest":
        if self.signed_amount is None and (self.org_id is None or self.service_id is None):
            raise InvalidUpdatingChannelParameters()
        return self
