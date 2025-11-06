import ast
import json
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator, model_validator
from web3 import Web3

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.application.schemas.queue_schema import QueueEventRequest
from deployer.constant import AUTH_PARAMETERS, AllowedRegistryEventNames
from deployer.exceptions import (
    InvalidServiceAuthParameters,
    MissingServiceEndpointException,
    MissingGithubParametersException,
    MissingServiceEventParameters,
)


class InitiateDeploymentRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")
    only_daemon: bool = Field(alias="onlyDaemon")
    service_endpoint: str = Field(alias="serviceEndpoint", default="")
    service_credentials: List[dict] = Field(alias="serviceCredentials", default=[])
    github_account_name: str = Field(alias="githubAccountName", default="")
    github_repository_name: str = Field(alias="githubRepositoryName", default="")

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "InitiateDeploymentRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)

    @field_validator("service_credentials")
    @classmethod
    def validate_credentials(cls, values: Optional[List[dict]]):
        if values:  # auth parameters are optional
            for value in values:
                for param in AUTH_PARAMETERS:
                    if param not in value.keys() or not value[param]:
                        raise InvalidServiceAuthParameters()
        return values

    @model_validator(mode="after")
    def validate_init_parameters(self):
        if self.only_daemon:
            if not self.service_endpoint:
                raise MissingServiceEndpointException()
        elif not self.github_account_name or not self.github_repository_name:
            raise MissingGithubParametersException()
        return self


class SearchDeploymentsRequest(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "SearchDeploymentsRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)


class RegistryEventConsumerRequest(BaseModel, QueueEventRequest):
    event_name: str = Field(alias="name")
    org_id: str = Field(alias="orgId")
    service_id: str | None = Field(alias="serviceId", default=None)
    metadata_uri: str | None = Field(alias="metadataURI", default=None)

    @classmethod
    @validation_handler()
    def validate_event(cls, event: dict) -> "RegistryEventConsumerRequest":
        return cls.model_validate(event)

    @model_validator(mode="before")
    @classmethod
    def convert_data_types(cls, data: dict) -> dict:
        data = cls.convert_data(data)
        converted_data = {}
        for key, value in data.items():
            new_value = value
            if key != "name":
                new_value = Web3.to_text(value).rstrip("\x00")
            converted_data[key] = new_value
        return converted_data

    @model_validator(mode="after")
    def validate_service_event(self):
        if self.event_name in AllowedRegistryEventNames:
            if not self.service_id or not self.metadata_uri:
                raise MissingServiceEventParameters()
        return self

    @classmethod
    def convert_data(cls, data: dict) -> dict:
        converted_data = {"name": data["name"], **ast.literal_eval(data["data"]["json_str"])}
        return converted_data
