from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from common.utils import dict_keys_to_camel_case


@dataclass
class BaseDomain:
    created_at: datetime
    updated_at: datetime

    def to_response(self) -> dict:
        result = asdict(self)

        del result["created_at"]
        del result["updated_at"]

        for k, v in result.items():
            if isinstance(v, Enum):
                result[k] = v.value
            elif isinstance(v, datetime):
                result[k] = v.isoformat()

        result = dict_keys_to_camel_case(result, recursively=True)
        return result
