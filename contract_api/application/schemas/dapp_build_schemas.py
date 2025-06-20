from pydantic import BaseModel, model_validator

from common.validation_handler import validation_handler
from contract_api.exceptions import MissingFilePathException


class TriggerDappBuildRequest(BaseModel):
    file_path: str

    @classmethod
    @validation_handler
    def validate_event(cls, event: dict) -> "TriggerDappBuildRequest":
        file_path = cls.get_file_path(event = event)
        return cls.model_validate({"file_path": file_path})

    @classmethod
    def get_file_path(cls, event: dict) -> str:
        try:
            file_path = event["Records"][0]['s3']['object']['key']
        except Exception as e:
            raise MissingFilePathException()
        return file_path

class NotifyDeployStatusRequest(BaseModel):
    org_id: str
    service_id: str
    build_status: int

    @classmethod
    @validation_handler
    def validate_event(cls, event: dict) -> "NotifyDeployStatusRequest":
        return cls.model_validate(**event)

    @model_validator(mode = 'before')
    @classmethod
    def validate(cls, data: dict) -> dict:
        data['build_status'] = int(data['build_status'])
        return data
