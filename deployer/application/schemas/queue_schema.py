import json


class QueueEventRequest:
    @classmethod
    def get_events_from_queue(cls, event: dict):
        converted_events = []
        records = event.get("Records", [])
        if records:
            for record in records:
                body = record.get("body")
                if body:
                    parsed_body = json.loads(body)
                    message = parsed_body.get("Message")
                    if message:
                        converted_events.append(json.loads(message))
        return converted_events