from datetime import UTC, datetime, timedelta

from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from deployer.domain.models.token_rate import NewTokenRateDomain
from deployer.infrastructure.models import TokenRate


class TokenRateRepository:
    @staticmethod
    def get_average_cogs_per_usd(session: Session, token_symbol: str) -> int:
        query = select(
            func.avg(TokenRate.cogs_per_usd).label("avg_cogs_per_usd"),
        ).where(TokenRate.token_symbol == token_symbol)

        result = session.execute(query).scalar_one()

        return int(result)

    @staticmethod
    def add_token_rate(session: Session, token_rate: NewTokenRateDomain) -> None:
        token_rate_db = TokenRate(
            token_symbol=token_rate.token_symbol,
            usd_per_token=token_rate.usd_per_token,
            cogs_per_usd=token_rate.cogs_per_usd,
        )

        session.add(token_rate_db)

    @staticmethod
    def delete_old_token_rates(session: Session) -> None:
        minimal_datetime = datetime.now(UTC) - timedelta(days=1)
        query = delete(TokenRate).where(TokenRate.created_at < minimal_datetime)

        session.execute(query)
