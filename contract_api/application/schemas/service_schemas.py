from pydantic import BaseModel, field_validator, model_validator, Field

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from contract_api.constant import SortKeys, SortOrder, FilterKeys
from contract_api.exceptions import InvalidSortParameter, InvalidOrderParameter, InvalidFilterParameter, \
    InvalidCurateParameter, InvalidAttributeParameter


class GetServiceFiltersRequest(BaseModel):
    attribute: str

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "GetServiceFiltersRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)

    @field_validator("attribute")
    @classmethod
    def validate_attribute(cls, value: str):
        if value not in FilterKeys:
            raise InvalidAttributeParameter()
        return value


class GetServicesRequest(BaseModel):
    limit: int
    page: int
    sort: str
    order: str
    filter: dict[str, bool | list[str]] = {}
    q: str = ""

    @classmethod
    @validation_handler([RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "GetServicesRequest":
        data = {**event[RequestPayloadType.BODY]}
        return cls.model_validate(data)

    @field_validator("sort")
    @classmethod
    def validate_sort(cls, value: str):
        if value not in SortKeys:
            raise InvalidSortParameter()
        return value

    @field_validator("order")
    @classmethod
    def validate_order(cls, value: str):
        if value not in SortOrder:
            raise InvalidOrderParameter()
        return value

    @field_validator("filter")
    @classmethod
    def validate_filter(cls, value: dict[str, str]):
        for key in value.keys():
            if key not in FilterKeys:
                raise InvalidFilterParameter()
        return value


class GetServiceRequest(BaseModel):
    org_id: str = Field(alias = "orgId")
    service_id: str = Field(alias = "serviceId")

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "GetServiceRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)


class CurateServiceRequest(BaseModel):
    org_id: str
    service_id: str
    curate: bool

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING])
    def validate_event(cls, event: dict) -> "CurateServiceRequest":
        data = {**event[RequestPayloadType.QUERY_STRING]}
        return cls.model_validate(data)

    @model_validator(mode = "before")
    @classmethod
    def validate_curate(cls, data: dict):
        if data['curate'] == 'true':
            data['curate'] = True
        elif data['curate'] == 'false':
            data['curate'] = False
        else:
            raise InvalidCurateParameter()
        return data


class SaveOffchainAttributeRequest(BaseModel):
    org_id: str
    service_id: str
    demo_component: dict

    @classmethod
    @validation_handler([RequestPayloadType.QUERY_STRING, RequestPayloadType.BODY])
    def validate_event(cls, event: dict) -> "SaveOffchainAttributeRequest":
        data = {**event[RequestPayloadType.QUERY_STRING], **event[RequestPayloadType.BODY]}
        return cls.model_validate(data)
