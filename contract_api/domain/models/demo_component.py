from dataclasses import dataclass


@dataclass
class DemoComponent:
    demo_component_url: str
    demo_component_required: int
    demo_component_status: str
    change_in_demo_component: int

    def __init__(self, demo_component_dict: dict):
        self.demo_component_url = demo_component_dict.get("demo_component_url", "")
        self.demo_component_required = demo_component_dict.get("demo_component_required", 0)
        self.demo_component_status = demo_component_dict.get("demo_component_status", "")
        self.change_in_demo_component = demo_component_dict.get("change_in_demo_component", 0)

    def to_dict(self):
        return {
                "demo_component_url": self.demo_component_url,
                "demo_component_required": str(self.demo_component_required),
                "demo_component_status": self.demo_component_status,
            }
