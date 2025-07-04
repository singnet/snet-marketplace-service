from common.exceptions import BadRequestException


class RequestContext:
    def __init__(self, event):
        self.event = event
        self.username = self._extract_username()
        self.origin = self._extract_origin()

    def _extract_username(self):
        try:
            return self.event["requestContext"]["authorizer"]["claims"]["email"]
        except KeyError:
            raise BadRequestException()

    def _extract_origin(self):
        try:
            origin = self.event["headers"].get("origin") or self.event["headers"].get("Origin")
            if not origin:
                raise BadRequestException()
            return origin
        except KeyError:
            raise BadRequestException()
