from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CallEventResponse(BaseModel):
    org_id: str = Field(alias="orgId")
    service_id: str = Field(alias="serviceId")
    duration: int
    amount: int
    timestamp: datetime


class GetCallEventsResponse(BaseModel):
    events: List[CallEventResponse]
    total_count: int = Field(alias="totalCount")
