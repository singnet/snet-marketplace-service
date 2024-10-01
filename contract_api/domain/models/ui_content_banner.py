from dataclasses import dataclass


@dataclass
class BannerEntityModel:

    id: int
    image: str
    image_alignment: str
    alt_text: str
    title: str
    description: str
    rank: int

    def to_response(self):
        response = {
            "id": self.id,
            "image": self.image,
            "alt_text": self.alt_text,
            "image_alignment": self.image_alignment,
            "title": self.title,
            "description": self.description
        }
        return response
