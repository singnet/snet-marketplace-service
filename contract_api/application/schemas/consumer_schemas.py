import ast
from pydantic import BaseModel, model_validator, Field, field_validator
import json
from web3 import Web3

from common.validation_handler import validation_handler


class EventConsumerRequest(BaseModel):
    event_name: str

    @classmethod
    def get_events_from_queue(cls, event: dict):
        converted_events = []
        records = event.get("Records", [])
        if records:
            for record in records:
                body = record.get("body")
                if body:
                    parsed_body = json.loads(body)
                    message = parsed_body.get("Message")
                    if message:
                        payload = json.loads(message)
                        converted_events.append(payload["blockchain_event"])
        return converted_events

    @model_validator(mode = 'before')
    @classmethod
    def convert_data(cls, data: dict) -> dict:
        converted_data = {
            "event_name": data["name"],
            **ast.literal_eval(data["data"]["json_str"])
        }
        return converted_data


class MpeEventConsumerRequest(EventConsumerRequest):
    channel_id: int = Field(alias = "channelId")
    group_id: str = Field(alias = "groupId")
    sender: str
    signer: str
    recipient: str
    nonce: int
    expiration: int
    amount: int

    @classmethod
    @validation_handler
    def validate_event(cls, event: dict) -> "MpeEventConsumerRequest":
        return cls.model_validate(**event)


class RegistryEventConsumerRequest(EventConsumerRequest):
    org_id: str = Field(alias = "orgId")
    service_id: str | None = Field(alias = "serviceId", default = None)
    metadata_uri: str | None = Field(alias = "metadataURI", default = None)

    @classmethod
    @validation_handler
    def validate_event(cls, event: dict) -> "RegistryEventConsumerRequest":
        return cls.model_validate(**event)

    @field_validator("org_id")
    @classmethod
    def convert_org_id(cls, value) -> str:
        return Web3.to_text(value).rstrip("\x00")

    @field_validator("service_id")
    @classmethod
    def convert_service_id(cls, value) -> str:
        return Web3.to_text(value).rstrip("\x00")

    @field_validator("metadata_uri")
    @classmethod
    def convert_metadata_uri(cls, value) -> str:
        return Web3.to_text(value).rstrip("\u0000")
