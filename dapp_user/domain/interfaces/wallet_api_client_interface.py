from abc import ABC, abstractmethod

from common.constant import TokenSymbol


class AbstractWalletsAPIClient(ABC):
    @abstractmethod
    def delete_user_wallet(self, username: str, token_name: TokenSymbol) -> bool: ...
