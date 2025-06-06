from common.exceptions import BadRequestException


class RequestContext:
    def __init__(self, event):
        self.event = event
        self.username = self._extract_username()

    def _extract_username(self):
        try:
            return self.event["requestContext"]["authorizer"]["claims"]["email"]
        except KeyError:
            raise BadRequestException()