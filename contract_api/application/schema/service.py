from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from common.exceptions import BadRequestException
from contract_api.infrastructure.models import ServiceMetadata


operator_mapping = {
    "IN": lambda column, value: column.in_(value),
    "EQ": lambda column, value: column == value[0],
    "NEQ": lambda column, value: column != value[0],
    "LIKE": lambda column, value: column.like(value[0]),
    "GT": lambda column, value: column > value[0],
    "GTE": lambda column, value: column >= value[0],
    "LT": lambda column, value: column < value[0],
    "LTE": lambda column, value: column <= value[0]
}

column_mapping = {
    "ranking": ServiceMetadata.ranking,
    "display_name": ServiceMetadata.display_name
}


class SortByEnum(Enum):
    RANKING = "ranking"
    DISPLAY_NAME = "display_name"


class OrderEnum(Enum):
    ASC = "asc"
    DESC = "desc"


class Sort(BaseModel):
    by: str
    order: OrderEnum


class FilterCondition(BaseModel):
    attribute: str
    operator: str
    value: List[str]


class GetServiceRequest(BaseModel):
    search: Optional[str] = None
    offset: int = Field(default=1, ge=1)
    limit: int = Field(default=30, ge=1)
    sort: Optional[Sort] = None
    filters: List[FilterCondition] = Field(default_factory=list) 


class AttributeNameEnum(Enum):
    ORG_ID = "org_id"
    TAG_NAME = "tag_name"
    DISPLAY_NAME = "display_name"

    @staticmethod
    def map_string_to_enum(attribute: str) -> 'AttributeNameEnum':
        try:
            return AttributeNameEnum(attribute)
        except ValueError:
            raise BadRequestException(f"Invalid attribute: {attribute}")