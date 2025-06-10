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
    org_uuid: Optional[str]
    service_uuid: Optional[str]


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

    @classmethod
    @model_validator(mode = "before")
    def headers_to_lower(cls, data: dict) -> dict:
        return {k.lower().replace("-", "_"): v for k, v in data.items()}

    @classmethod
    @field_validator("content_type")
    def validate_content_type(cls, v):
        if v not in settings.files.ALLOWED_CONTENT_TYPE:
            raise InvalidContentType()
        return v

    @classmethod
    @field_validator("type")
    def validate_upload_type(cls, v):
        if v not in UPLOAD_TYPE_DETAILS:
            raise InvalidUploadType()
        return v

    @classmethod
    @field_validator("raw_file_data")
    def validate_file_data(cls, v):
        if len(v) == 0:
            raise EmptyFileException()
        return base64.b64decode(v)

    @classmethod
    @model_validator(mode = "after")
    def validate_query_params(cls, data: dict) -> dict:
        for key in UPLOAD_TYPE_DETAILS[data["type"]]["required_query_params"]:
            if key not in data:
                raise MissingUploadTypeDetailsParams()
        return data

class ManageProtoCompilationRequest(BaseModel):
    input_s3_path: str
    output_s3_path: str
    org_id: str
    service_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "ManageProtoCompilationRequest":
        try:
            return cls.model_validate(event)
        except (ValidationError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()

class GeneratePythonStubsRequest(BaseModel):
    input_s3_path: str
    output_s3_path: str
    org_id: str
    service_id: str

    @classmethod
    def validate_event(cls, event: dict) -> "GeneratePythonStubsRequest":
        try:
            return cls.model_validate(event)
        except (ValidationError, json.JSONDecodeError, KeyError):
            raise PayloadValidationError()