from abc import ABC, abstractmethod

from common.constant import TokenSymbol


class AbstractContractAPIClient(ABC):
    @abstractmethod
    def update_service_rating(
        self,
        org_id: str,
        service_id: str,
        rating: float,
        total_users_rated: int,
        token_name: TokenSymbol,
    ) -> None: ...
