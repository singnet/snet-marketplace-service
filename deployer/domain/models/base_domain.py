from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


@dataclass
class BaseDomain:
    created_at: datetime
    updated_at: datetime

    def to_response(self):
        result = asdict(self)
        del result["created_at"]
        del result["updated_at"]
        for k, v in result.items():
            if isinstance(v, Enum):
                result[k] = v.value
        return result
