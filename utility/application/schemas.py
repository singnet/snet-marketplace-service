import base64
from pydantic import BaseModel, field_validator, model_validator, Field

from common.constant import RequestPayloadType
from common.validation_handler import validation_handler
from utility.settings import settings
from utility.constants import UPLOAD_TYPE_DETAILS
from utility.exceptions import (
    InvalidContentType,
    InvalidUploadType,
    EmptyFileException,
    MissingUploadTypeDetailsParams,
)


class UploadFileRequest(BaseModel):
    content_type: str = Field(alias="content-type")
    type: str
    raw_file_data: bytes
    org_uuid: str | None = None
    service_uuid: str | None = None

    @classmethod
    @validation_handler(
        [
            RequestPayloadType.QUERY_STRING,
            RequestPayloadType.HEADERS,
            RequestPayloadType.QUERY_STRING,
        ]
    )
    def validate_event(cls, event: dict) -> "UploadFileRequest":
        data = {
            "raw_file_data": event[RequestPayloadType.BODY],
            **event[RequestPayloadType.HEADERS],
            **event[RequestPayloadType.QUERY_STRING],
        }
        return cls.model_validate(data)

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        if v not in settings.files.ALLOWED_CONTENT_TYPE:
            raise InvalidContentType()
        return v

    @field_validator("type")
    @classmethod
    def validate_upload_type(cls, v):
        if v not in UPLOAD_TYPE_DETAILS:
            raise InvalidUploadType()
        return v

    @field_validator("raw_file_data")
    @classmethod
    def validate_file_data(cls, v):
        if len(v) == 0:
            raise EmptyFileException()
        return base64.b64decode(v)

    @model_validator(mode="after")
    def validate_query_params(self) -> "UploadFileRequest":
        for key in UPLOAD_TYPE_DETAILS[self.type]["required_query_params"]:
            if key not in self.__dict__ or getattr(self, key) is None:
                raise MissingUploadTypeDetailsParams()
        return self


class StubsGenerationRequest(BaseModel):
    input_s3_path: str
    output_s3_path: str
    org_id: str
    service_id: str

    @classmethod
    @validation_handler()
    def validate_event(cls, event: dict) -> "StubsGenerationRequest":
        return cls.model_validate(event)
