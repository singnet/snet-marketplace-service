import json
from datetime import datetime as dt


class DemoComponent:
    def __init__(self, demo_component_required, demo_component_url="", demo_component_status=""):
        self._demo_component_url = demo_component_url
        self._demo_component_required = demo_component_required
        self._demo_component_status = demo_component_status

    def to_dict(self, last_modified=None):
        return {
            "demo_component_url": self._demo_component_url,
            "demo_component_required": self._demo_component_required,
            "demo_component_status": self._demo_component_status,
            "demo_component_last_modified": last_modified if last_modified else ""
        }

    @property
    def demo_component_url(self):
        return self._demo_component_url

    @demo_component_url.setter
    def demo_component_url(self, demo_component_url):
        self._demo_component_url = demo_component_url

    @property
    def demo_component_required(self):
        return self._demo_component_required

    @demo_component_required.setter
    def demo_component_required(self, demo_component_required):
        self._demo_component_required = demo_component_required

    @property
    def demo_component_status(self):
        return self._demo_component_status

    @demo_component_status.setter
    def demo_component_status(self, demo_component_status):
        self._demo_component_status = demo_component_status