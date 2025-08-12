from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


@dataclass
class BaseDomain:
    created_on: datetime
    updated_on: datetime

    def to_response(self):
        result = asdict(self)
        del result["created_on"]
        del result["updated_on"]
        for k, v in result.items():
            if isinstance(v, Enum):
                result[k] = v.value
        return result