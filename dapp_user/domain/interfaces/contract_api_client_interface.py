from abc import ABC, abstractmethod


class AbstractContractAPIClient(ABC):
    @abstractmethod
    def update_service_rating(
        self,
        org_id: str,
        service_id: str,
        rating: float,
        total_users_rated: int,
    ) -> None: ...
