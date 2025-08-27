import json
from typing import List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic import ValidationError

from common.constant import PayloadAssertionError, RequestPayloadType
from common.exceptions import BadRequestException
from registry.constants import EnvironmentType, DEFAULT_SERVICE_RANKING, ServiceType
from registry.infrastructure.storage_provider import StorageProviderType


class VerifyServiceIdRequest(BaseModel):
    org_uuid: str
    service_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "VerifyServiceIdRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, (
                PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS.value)

            query_string_parameters = event[RequestPayloadType.QUERY_STRING]
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**path_parameters, **query_string_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class SaveTransactionHashRequest(BaseModel):
    org_uuid: str
    service_uuid: str
    transaction_hash: str | None = None

    @classmethod
    def validate_event(cls, event: dict) -> "SaveTransactionHashRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class SaveServiceRequest(BaseModel):
    org_uuid: str
    service_uuid: str

    service_id: str
    proto: dict = Field(default_factory=dict)
    storage_provider: str | None = Field(default="")
    display_name: str | None = Field(default="")
    short_description: str | None = Field(default="")
    description: str | None = Field(default="")
    project_url: str | None = Field(default="")
    service_type: str | None = Field(default=ServiceType.GRPC.value)
    contributors: list = Field(default_factory=list)
    tags: list = Field(default_factory=list)
    mpe_address: str | None = Field(default="")
    groups: list = Field(default_factory=list)
    transaction_hash: str | None = Field(default="")
    comments: dict = Field(default_factory=dict)
    assets: dict = Field(default_factory=dict)

    @classmethod
    def validate_event(cls, event: dict) -> "SaveServiceRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class SaveServiceGroupsRequest(BaseModel):
    org_uuid: str
    service_uuid: str
    groups: List[dict] = Field(min_length=1, default_factory=list)

    @classmethod
    def validate_event(cls, event: dict) -> "SaveServiceGroupsRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class CreateServiceRequest(BaseModel):
    org_uuid: str

    service_id: str = Field(default="")
    proto: dict = Field(default_factory=dict)
    storage_provider: str | None = Field(default="")
    display_name: str | None = Field(default="")
    short_description: str | None = Field(default="")
    description: str | None = Field(default="")
    project_url: str | None = Field(default="")
    service_type: str | None = Field(default=ServiceType.GRPC.value)
    contributors: list = Field(default_factory=list)
    tags: list = Field(default_factory=list)
    mpe_address: str | None = Field(default="")
    groups: list = Field(default_factory=list)
    transaction_hash: str | None = Field(default="")
    comments: dict = Field(default_factory=dict)
    assets: dict = Field(default_factory=dict)
    ranking: int = Field(default=DEFAULT_SERVICE_RANKING)
    rating: dict = Field(default_factory=dict)
    metadata_uri: str = Field(default="")

    @classmethod
    def validate_event(cls, event: dict) -> "CreateServiceRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class GetServicesForOrganizationRequest(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    org_uuid: str
    offset: int = Field(default=0)
    limit: int = Field(default=10)
    search_string: str | None = Field(default="", alias="q")
    search_attribute: str | None = Field(default="", alias="s")
    sort_by: str | None = None
    order_by: str | None = None
    filters: list | None = Field(default_factory=list)

    @classmethod
    def validate_event(cls, event: dict) -> "GetServicesForOrganizationRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class GetServiceRequest(BaseModel):
    org_uuid: str
    service_uuid: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetServiceRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            path_parameters = event[RequestPayloadType.PATH_PARAMS]
            return cls.model_validate(path_parameters)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class GetDaemonConfigRequest(BaseModel):
    org_uuid: str
    service_uuid: str
    network: EnvironmentType

    @classmethod
    def validate_event(cls, event: dict) -> "GetDaemonConfigRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, (
                PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS.value)

            query_string_parameters = event[RequestPayloadType.QUERY_STRING]
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**query_string_parameters, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class ServiceDeploymentStatusRequest(BaseModel):
    org_id: str
    service_id: str
    build_status: int

    @classmethod
    def validate_event(cls, event: dict) -> "ServiceDeploymentStatusRequest":
        try:
            return cls.model_validate(event)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class GetCodeBuildStatusRequest(BaseModel):
    org_uuid: str
    service_uuid: str

    @classmethod
    def validate_event(cls, event: dict) -> "GetCodeBuildStatusRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)

            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            return cls.model_validate(path_parameters)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")


class PublishServiceRequest(BaseModel):
    org_uuid: str
    service_uuid: str
    storage_provider: StorageProviderType = StorageProviderType.IPFS
    lighthouse_token: str | None = None

    @model_validator(mode="after")
    def check_lighthouse_token_required(cls, model):
        if model.storage_provider == "filecoin" and model.lighthouse_token is None:
            raise ValueError("lighthouse_token is required when storage_provider is 'filecoin'")
        return model

    @classmethod
    def validate_event(cls, event: dict) -> "PublishServiceRequest":
        try:
            assert event.get(RequestPayloadType.PATH_PARAMS) is not None, (
                PayloadAssertionError.MISSING_PATH_PARAMETERS.value)
            assert event.get(RequestPayloadType.BODY) is not None, (
                PayloadAssertionError.MISSING_BODY.value)

            body = json.loads(event[RequestPayloadType.BODY])
            path_parameters = event[RequestPayloadType.PATH_PARAMS]

            data = {**body, **path_parameters}

            return cls.model_validate(data)

        except ValidationError as e:
            missing_params = [x["loc"][0] for x in e.errors()]
            raise BadRequestException(message = f"Missing required parameters: "
                                                f"{', '.join(missing_params)}")
        except AssertionError as e:
            raise BadRequestException(message = str(e))
        except Exception:
            raise BadRequestException(message = "Error while parsing payload")
