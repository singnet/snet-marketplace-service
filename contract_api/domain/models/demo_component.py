from dataclasses import dataclass


@dataclass
class DemoComponentEntityModel:

    demo_component_url: str
    demo_component_required: str
    demo_component_status: str

    def to_dict(self):
        return {
                "demo_component_url": self._demo_component_url,
                "demo_component_required": self._demo_component_required,
                "demo_component_status": self._demo_component_status,
            }
