import base64
from typing import Optional

from pydantic import BaseModel, ValidationError, field_validator, model_validator
import json

from common.constant import PayloadAssertionError, RequestPayloadType
from common.schemas import PayloadValidationError
from utility.settings import settings
from utility.constants import UPLOAD_TYPE_DETAILS
from utility.exceptions import InvalidContentType, InvalidUploadType, EmptyFileException, MissingUploadTypeDetailsParams


class UploadFileRequest(BaseModel):
    content_type: str
    type: str
    raw_file_data: bytes
    org_uuid: Optional[str] = None
    service_uuid: Optional[str] = None

    @classmethod
    def validate_event(cls, event: dict) -> "UploadFileRequest":
        try:
            assert event.get(RequestPayloadType.QUERY_STRING) is not None, PayloadAssertionError.MISSING_QUERY_STRING_PARAMETERS
            assert event.get(RequestPayloadType.BODY) is not None, PayloadAssertionError.MISSING_BODY
            assert event.get(RequestPayloadType.HEADERS) is not None, PayloadAssertionError.MISSING_HEADERS

            data = {"raw_file_data": event[RequestPayloadType.BODY], **event[RequestPayloadType.HEADERS], **event[RequestPayloadType.QUERY_STRING]}
            return cls.model_validate(data)

        except (ValidationError, json.JSONDecodeError, AssertionError, KeyError):
            raise PayloadValidationError()

    @model_validator(mode = "before")
    @classmethod
    def headers_to_lower(cls, data: dict) -> dict:
        return {k.lower().replace("-", "_"): v for k, v in data.items()}

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

    @model_validator(mode = "after")
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
    def validate_event(cls, event: dict) -> "StubsGenerationRequest":
        try:
            return cls.model_validate(event)
        except (ValidationError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()
