import json

from pydantic import BaseModel, Field, model_validator

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from deployer.application.schemas.queue_schema import QueueEventRequest
from deployer.constant import HaaSDeploymentStatus
from deployer.exceptions import MissingCommitHashParameter


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
    status: HaaSDeploymentStatus
    commit_hash: str = Field(alias="commitHash", default="")

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "UpdateHostedServiceStatusRequest":
        body = json.loads(event[RequestPayloadType.BODY])
        return cls.model_validate(body)

    @model_validator(mode="after")
    def validate_commit_hash(self):
        if self.status == HaaSDeploymentStatus.STARTING and not self.commit_hash:
            raise MissingCommitHashParameter()
        return self


class CheckGithubRepositoryRequest(BaseModel):
    account_name: str = Field(alias="accountName")
    repository_name: str = Field(alias="repositoryName")

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "CheckGithubRepositoryRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)
