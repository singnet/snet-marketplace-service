from datetime import datetime as dt


class DemoComponent:
    def __init__(self, url, required, status, last_modified):
        self._url = url
        self._required = required
        self._status = status
        self._last_modified = last_modified

    def to_dict(self):
        return {
            "url": self._url,
            "required": self._required,
            "status": self._status,
            "last_modified": dt.fromisoformat(self._last_modified) if self._last_modified else None
        }

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def required(self):
        return self._required

    @required.setter
    def org_id(self, required):
        self._required = required

    @property
    def status(self):
        return self._status

    @status.setter
    def service_id(self, status):
        self._status = status

    @property
    def last_modified(self):
        return self._last_modified

    @last_modified.setter
    def service_row_id(self, last_modified):
        self._last_modified = last_modified
