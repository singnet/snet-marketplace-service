class DemoComponent:
    def __init__(self, demo_component_required, demo_component_url):
        self._demo_component_url = demo_component_url
        self._demo_component_required = demo_component_required

    def to_dict(self):
        return {
            "demo_component_url": self._demo_component_url,
            "demo_component_required": self._demo_component_required,
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

