from abc import ABC, abstractmethod


class AbstractWalletsAPIClient(ABC):
    @abstractmethod
    def delete_user_wallet(self, username: str) -> bool: ...
