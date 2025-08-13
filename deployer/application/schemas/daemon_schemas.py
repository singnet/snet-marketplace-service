from pydantic import BaseModel, Field

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler


class DaemonRequest(BaseModel):
    daemon_id: str = Field(alias="daemonId")

    @classmethod
    @validation_handler([RequestPayloadType.PATH_PARAMS])
    def validate_event(cls, event: dict) -> "DaemonRequest":
        data = {**event[RequestPayloadType.PATH_PARAMS]}
        return cls.model_validate(data)
