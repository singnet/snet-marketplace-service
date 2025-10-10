from dataclasses import dataclass

from deployer.domain.models.base_domain import BaseDomain


@dataclass
class NewTokenRateDomain:
    token_symbol: str
    usd_per_token: float
    cogs_per_usd: int


@dataclass
class TokenRateDomain(NewTokenRateDomain, BaseDomain):
    id: int
