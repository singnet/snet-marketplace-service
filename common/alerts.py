import json
import requests
from abc import ABC, abstractmethod
from functools import wraps
from common.logger import get_logger


logger = get_logger(__name__)


def delivery_exception_handler(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            self.health_check()
            return method(self, *args, **kwargs)
        except AssertionError as e:
            logger.warning(f"Failed to send alert ({e})", exc_info=False)
        except Exception as e:
            logger.warning(f"Failed to send alert ({repr(e)})", exc_info=True)

    return wrapper


def format_handler_event_error_header(handler_name, event, **kwargs):
    path = event.get("path", None)
    path_parameters = event.get("pathParameters", None)
    query_string_parameters = event.get("queryStringParameters", None)
    body = event.get("body", None)
    environment = kwargs.get("environment", None)
    error_message = ""
    error_message += "Error Reported!\n"
    error_message += f"Environment: {environment}\n" if environment else ""
    error_message += f"Handler: {handler_name}\n"
    error_message += f"Path: {path}\n" if path else ""
    error_message += f"pathParameters: {path_parameters}\n" if path_parameters else ""
    error_message += (
        f"queryStringParameters: {query_string_parameters}\n"
        if query_string_parameters
        else ""
    )
    error_message += f"body: {body}\n" if body else ""
    return error_message


class AlertsProcessor(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Set the name of the alerts processor for external logging and debug"""
        return "Abstract"

    @abstractmethod
    def __init__(self):
        """Definition of all the parameters required to deliver notifications to the alert channel"""
        pass

    @abstractmethod
    def health_check(self):
        """Check that all processor parameters are set correctly for successful delivery
        !!! For each check use only assertions without AssertionError handling
        """
        assert True, (
            "Check not passed"
        )  # Use constructions like this to check all important points

    @abstractmethod
    def send(self, message: str):
        """Main method to deliver notification message to the alert channel"""
        pass

    def send_handler_event_error(self, handler_name, event, error_message, **kwargs):
        error_header = format_handler_event_error_header(handler_name, event, **kwargs)
        message = f"{error_header}{error_message}"
        self.send(message)


class DefaultProcessor(AlertsProcessor):
    @property
    def name(self):
        return "Default"

    def __init__(self):
        """Initialize the default processor. Does not require any arguments; uses only the logger."""
        pass

    def health_check(self):
        """Performs a health check. No arguments needed; relies only on the logger."""
        pass

    def send(self, message: str):
        """Logs an error message using the default logger."""
        logger.error(message)


class SlackProcessor(AlertsProcessor):
    @property
    def name(self):
        return "Slack"

    def __init__(self, url, channel, username="webhookbot", icon=":ghost:"):
        self.url = url
        self.channel = channel
        self.username = username
        self.icon = icon

    def health_check(self):
        assert self.url and isinstance(self.url, str), "Bad slack url value"
        assert self.channel and isinstance(self.channel, str), "Bad slack channel value"

    @delivery_exception_handler
    def send(self, message: str):
        logger.info(f"Sending slack notification to #{self.channel}")
        payload = {
            "channel": f"#{self.channel}",
            "username": self.username,
            "icon_emoji": self.icon,
            "text": message,
        }
        response = requests.post(url=self.url, data=json.dumps(payload))
        logger.info(f"Slack response [code {response.status_code}]: {response.text}")


class MattermostProcessor(AlertsProcessor):
    @property
    def name(self):
        return "Mattermost"

    def __init__(self, url):
        self.url = url

    def health_check(self):
        assert self.url and isinstance(self.url, str), "Bad mattermost url value"

    @delivery_exception_handler
    def send(self, message: str):
        headers = {"Content-Type": "application/json"}
        payload = {"text": message}
        response = requests.post(self.url, headers=headers, data=json.dumps(payload))
        logger.info(
            f"Mattermost response [code {response.status_code}]: {response.text}"
        )
