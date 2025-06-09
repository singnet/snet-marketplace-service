from signer.infrastructure.repositories.base_repository import BaseRepository
from signer.infrastructure.models import FreeCallTokenInfo
from signer.domain.free_call_token import FreeCallTokenInfoEntity


class FreeCallTokenInfoRepository(BaseRepository):
    def get_free_call_token_info_by_username(
        self,
        username: str,
        organization_id: str,
        service_id: str,
        group_id: str,
    ) -> FreeCallTokenInfoEntity | None:
        db_token = (
            self.session.query(FreeCallTokenInfo)
            .filter_by(
                username=username,
                organization_id=organization_id,
                service_id=service_id,
                group_id=group_id,
            )
            .first()
        )

        return (
            FreeCallTokenInfoEntity(
                username=db_token.username,
                organization_id=db_token.organization_id,
                service_id=db_token.service_id,
                group_id=db_token.group_id,
                token=db_token.token,
                expiration_block_number=db_token.expiration_block_number,
            )
            if db_token
            else None
        )

    @BaseRepository.write_ops
    def insert_or_update_free_call_token_info(
        self,
        username: str,
        organization_id: str,
        service_id: str,
        group_id: str,
        expiration_block_number: int,
        new_token: bytes,
    ) -> FreeCallTokenInfoEntity:
        db_token = (
            self.session.query(FreeCallTokenInfo)
            .filter_by(
                username=username,
                organization_id=organization_id,
                service_id=service_id,
                group_id=group_id,
            )
            .first()
        )

        if db_token:
            db_token.expiration_block_number = expiration_block_number
            db_token.token = new_token
            self.session.commit()
        else:
            db_token = FreeCallTokenInfo(
                username=username,
                organization_id=organization_id,
                service_id=service_id,
                group_id=group_id,
                token=new_token,
                expiration_block_number=expiration_block_number,
            )
            self.session.add(db_token)
            self.session.commit()

        return FreeCallTokenInfoEntity(
            username=db_token.username,
            organization_id=db_token.organization_id,
            service_id=db_token.service_id,
            group_id=db_token.group_id,
            token=db_token.token,
            expiration_block_number=db_token.expiration_block_number,
        )
