from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BaseDomain:
    row_id: int
    created_on: datetime
    updated_on: datetime

    def to_response(self):
        result = asdict(self)
        del result["row_id"]
        del result["created_on"]
        del result["updated_on"]
        if "service_row_id" in result:
            del result["service_row_id"]
        return result