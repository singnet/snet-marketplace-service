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


# class DemoComponent:
#     def __init__(self, demo_component_required, demo_component_url="", demo_component_status=""):
#         self._demo_component_url = demo_component_url
#         self._demo_component_required = demo_component_required
#         self._demo_component_status = demo_component_status
#
#     def to_dict(self):
#         return {
#                 "demo_component_url": self._demo_component_url,
#                 "demo_component_required": self._demo_component_required,
#                 "demo_component_status": self._demo_component_status,
#             }
#
#     @property
#     def demo_component_url(self):
#         return self._demo_component_url
#
#     @demo_component_url.setter
#     def demo_component_url(self, demo_component_url):
#         self._demo_component_url = demo_component_url
#
#     @property
#     def demo_component_required(self):
#         return self._demo_component_required
#
#     @demo_component_required.setter
#     def demo_component_required(self, demo_component_required):
#         self._demo_component_required = demo_component_required
#
#     @property
#     def demo_component_status(self):
#         return self._demo_component_status
#
#     @demo_component_status.setter
#     def demo_component_status(self, demo_component_status):
#         self._demo_component_status = demo_component_status
