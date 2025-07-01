from dataclasses import dataclass, asdict


@dataclass
class BaseDomain:
    def to_response(self):
        result = asdict(self)
        del result["row_id"]
        del result["created_on"]
        del result["updated_on"]
        if "service_row_id" in result:
            del result["service_row_id"]
        return result