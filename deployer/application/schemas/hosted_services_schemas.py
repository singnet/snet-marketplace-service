import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.application.schemas.queue_schema import QueueEventRequest
from deployer.constant import HaaSServiceStatus
from deployer.exceptions import InvalidHaasServiceStatusParameter, MissingCommitHashParameter


class HostedServiceRequest(BaseModel):
    hosted_service_id: str = Field(alias="hostedServiceId")

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "HostedServiceRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)


class UpdateHostedServiceStatusRequest(BaseModel, QueueEventRequest):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")
    status: str
    commit_hash: Optional[str] = Field(alias="commitHash", default=None)

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "UpdateHostedServiceStatusRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in HaaSServiceStatus:
            raise InvalidHaasServiceStatusParameter()
        return value

    @model_validator(mode="after")
    def validate_commit_hash(self):
        if self.status == HaaSServiceStatus.RESTARTING and self.commit_hash is None:
            raise MissingCommitHashParameter()
        return self
