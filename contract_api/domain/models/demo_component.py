from dataclasses import dataclass


@dataclass
class DemoComponent:
    demo_component_url: str = ""
    demo_component_required: int = 0
    demo_component_status: str = ""
    change_in_demo_component: int = 0

    def to_short_dict(self):
        return {
                "demo_component_url": self.demo_component_url,
                "demo_component_required": str(self.demo_component_required),
                "demo_component_status": self.demo_component_status,
            }
