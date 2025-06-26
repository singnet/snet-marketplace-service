from abc import ABC, abstractmethod
from typing import List

from dapp_user.domain.models.user import NewUser


class UserIdentityManager(ABC):
    @abstractmethod
    def get_all_users(self) -> List[NewUser]:
        """Fetch all users from the identity provider"""
        pass
