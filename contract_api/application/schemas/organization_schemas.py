from pydantic import BaseModel

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler


class GetAllOrganizationsRequest(BaseModel):
    pass


class GetGroupRequest(BaseModel):
    org_id: str
    group_id: str

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "GetGroupRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)


