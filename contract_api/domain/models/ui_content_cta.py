from dataclasses import dataclass


@dataclass
class CTAEntityModel:

    id: int
    text: str
    url: str
    type: str
    variant: str
    rank: int

    def to_dict(self):
        response = {
            "id": self.id,
            "text": self.text,
            "url": self.url,
            "type": self.type,
            "rank": self.rank
        }

        return response
