from typing import Union

from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime as dt

from wallets.domain.models.user_wallet import UserWalletModel
from wallets.domain.models.wallet import WalletModel
from wallets.infrastructure.repositories.base_repository import BaseRepository
from wallets.domain.wallets_factory import WalletsFactory
from wallets.infrastructure.models import Wallet, UserWallet

from common.logger import get_logger


logger = get_logger(__name__)


class WalletRepository(BaseRepository):

    def add_user_for_wallet(self, wallet: Union[Wallet, WalletModel, UserWallet, UserWalletModel], username: str):
        try:
            is_default = 0
            time_now = dt.utcnow()
            user_wallet = UserWallet(
                username = username,
                address = wallet.address,
                is_default = is_default,
                row_created = time_now,
                row_updated = time_now
            )
            self.session.add(user_wallet)
            self.session.commit()
            logger.info(f"Successfully linked user {username} to wallet {wallet.address}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to link user to wallet: {e}")
            raise Exception("Failed to link user to the wallet")

    def get_wallet_details(self, wallet: Union[Wallet, WalletModel]):
        try:
            wallet_db = self.session.query(Wallet).filter(Wallet.address == wallet.address).first()
            if not wallet_db:
                return None
            return WalletsFactory.convert_wallet_db_model_to_entity_model(wallet_db)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def insert_wallet(self, wallet: Union[Wallet, WalletModel]):
        try:
            time_now = dt.utcnow()
            wallet_db = Wallet(
                address = wallet.address,
                type = wallet.type,
                encrypted_key = wallet.encrypted_key,
                status = wallet.status,
                row_created = time_now,
                row_updated = time_now
            )
            self.session.add(wallet_db)
            self.session.commit()
            logger.info(f"Successfully inserted wallet {wallet.address}")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to insert wallet: {e}")
            raise Exception("Failed to insert the wallet")

    def get_wallet_data_by_username(self, username: str) -> list[tuple[UserWalletModel, WalletModel]]:
        try:
            wallets_data = self.session.query(
                UserWallet,
                Wallet
            ).join(
                Wallet, UserWallet.address == Wallet.address
            ).filter(
                UserWallet.username == username
            ).all()
            wallets = []
            for wallet_data in wallets_data:
                wallet = WalletsFactory.convert_wallet_db_model_to_entity_model(wallet_data.Wallet)
                user_wallet = WalletsFactory.convert_user_wallet_db_model_to_entity_model(wallet_data.UserWallet)
                wallets.append((user_wallet, wallet))
            return wallets
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def set_default_wallet(self, username: str, address: str):
        try:
            self.session.begin()
            # Set the specified wallet as default
            self.session.query(UserWallet).filter(
                UserWallet.username == username,
                UserWallet.address == address
            ).update({"is_default": 1})
            # Set all other wallets as non-default
            self.session.query(UserWallet).filter(
                UserWallet.username == username,
                UserWallet.address != address
            ).update({"is_default": 0})
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Unable to set default wallet as {address} for username {username}. Failed to set default wallet: {e}")
            raise Exception(f"Unable to set default wallet as {address} for username {username}")

    def remove_user_wallet(self, username: str):
        try:
            self.session.query(UserWallet).filter(
                UserWallet.username == username
            ).delete()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
