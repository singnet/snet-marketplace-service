class UserRepositoryException(Exception):
    """Base exception for user repository errors."""

    pass


class UserNotFoundException(UserRepositoryException):
    """Exception raised when a user is not found in the repository."""

    def __init__(self, username: str):
        super().__init__(f"User with username '{username}' not found.")


class FeedbackAlreadyExistsException(UserRepositoryException):
    """Exception raised when a feedback is already exists in the repository"""

    def __init__(self):
        super().__init__("User feedback is already exists")


class VoteAlreadyExistsException(UserRepositoryException):
    """Exception raised when a vote is already exists in the repository"""

    def __init__(self):
        super().__init__("User vote is already exists")


class InvalidUpdateRequest(UserRepositoryException):
    """Raised when update_user is called without any fields to update."""

    def __init__(self):
        super().__init__("At least one field (email_alerts or is_terms_accepted) must be provided.")


class UserAlreadyExistsException(UserRepositoryException):
    """Exception raised when trying to create a user that already exists."""

    def __init__(self, username: str):
        super().__init__(f"User with username '{username}' already exists.")


class UserPreferenceNotFoundException(UserRepositoryException):
    """Exception raised when a user preference is not found."""

    def __init__(self, user_row_id: int):
        super().__init__(f"User preference for user with row ID '{user_row_id}' not found.")


class UserPreferenceAlreadyExistsException(UserRepositoryException):
    """Exception raised when trying to create a user preference that already exists."""

    def __init__(
        self, user_row_id: int, preference_type: str, communication_type: str, source: str
    ):
        super().__init__(
            f"User preference for user with row ID '{user_row_id}', "
            f"preference type '{preference_type}', "
            f"communication type '{communication_type}', "
            f"and source '{source}' already exists."
        )
