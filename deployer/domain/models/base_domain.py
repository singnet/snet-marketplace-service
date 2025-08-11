from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BaseDomain:
    created_on: datetime
    updated_on: datetime

    def to_response(self):
        result = asdict(self)
        del result["created_on"]
        del result["updated_on"]
        return result