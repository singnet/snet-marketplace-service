import json
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.application.schemas.queue_schema import QueueEventRequest
from deployer.constant import AUTH_PARAMETERS, HaaSDeploymentStatus
from deployer.exceptions import InvalidServiceAuthParameters


class DaemonRequest(BaseModel):
    daemon_id: str = Field(alias="daemonId")

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "DaemonRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)


class UpdateConfigRequest(BaseModel):
    daemon_id: str = Field(alias="daemonId")
    service_endpoint: Optional[str] = Field(alias="serviceEndpoint", default=None)
    service_credentials: Optional[List[dict]] = Field(alias="serviceCredentials", default=None)

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS, RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "UpdateConfigRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        data = {**event[RequestPayloadType.PATH_PARAMS], **body}
        return cls.model_validate(data)

    @field_validator("service_credentials")
    @classmethod
    def validate_credentials(cls, values: Optional[List[dict]]):
        if values is not None:  # auth parameters are optional
            for value in values:
                for param in AUTH_PARAMETERS:
                    if param not in value.keys() or not value[param]:
                        raise InvalidServiceAuthParameters()
        return values


class SearchDaemonRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "SearchDaemonRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)


class UpdateDaemonStatusRequest(BaseModel, QueueEventRequest):
    org_id: str = Field(alias = "orgId")
    service_id: str = Field(alias = "serviceId")
    status: HaaSDeploymentStatus

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "UpdateDaemonStatusRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)
