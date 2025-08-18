import json
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.constant import AUTH_PARAMETERS
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
    service_endpoint: Optional[str] = Field(alias = "serviceEndpoint", default = None)
    auth_parameters: Optional[dict] = Field(alias = "authParameters", default = None)

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS, RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "UpdateConfigRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        data = {**event[RequestPayloadType.PATH_PARAMS], **body}
        return cls.model_validate(data)

    @field_validator("auth_parameters")
    @classmethod
    def validate_auth_parameters(cls, value: Optional[dict]):
        if value is not None:  # auth parameters are optional
            for param in AUTH_PARAMETERS:
                if param not in value.keys() or not value[param]:
                    raise InvalidServiceAuthParameters()


class SearchDaemonRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "SearchDaemonRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)
