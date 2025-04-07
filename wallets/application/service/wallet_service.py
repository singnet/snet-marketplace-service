from cryptography.fernet import Fernet

# from common.blockchain_util import BlockChainUtil
from wallets.infrastructure.blockchain_util import BlockChainUtil
"""
Temporarily moved for latest web3 version for python 3.12
TODO: change back when 'common' is updated
"""
from common.boto_utils import BotoUtils
from common.logger import get_logger
from common.utils import Utils
from wallets.config import NETWORK_ID, NETWORKS, REGION_NAME, ENCRYPTION_KEY
from wallets.constant import GENERAL_WALLET_TYPE, WalletStatus
from wallets.domain.models.wallet import WalletModel
from wallets.infrastructure.repositories.wallet_repository import WalletRepository


logger = get_logger(__name__)


class WalletService:
    def __init__(self):
        self.boto_utils = BotoUtils(region_name=REGION_NAME)
        self.blockchain_util = BlockChainUtil(
            provider_type="HTTP_PROVIDER",
            provider=NETWORKS[NETWORK_ID]['http_provider']
        )
        self.utils = Utils()
        self.wallet_repo = WalletRepository()
        self.ENCRYPTION_KEY = self.boto_utils.get_ssm_parameter(ENCRYPTION_KEY)
        self.fernet = Fernet(bytes.fromhex(self.ENCRYPTION_KEY))

    def create_and_register_wallet(self, username):
        address, private_key = self.blockchain_util.create_account()
        encrypted_key = self._encrypt_key(private_key)
        wallet = WalletModel(address=address, encrypted_key=encrypted_key,
                        type=GENERAL_WALLET_TYPE, status=WalletStatus.ACTIVE.value)
        self._register_wallet(wallet, username)
        wallet = wallet.to_response()
        wallet["private_key"] = private_key
        return wallet

    def _register_wallet(self, wallet, username):
        existing_wallet = self.wallet_repo.get_wallet_details(wallet)
        if existing_wallet is None:
            self.wallet_repo.insert_wallet(wallet)
        self.wallet_repo.add_user_for_wallet(wallet, username)

    def register_wallet(self, wallet_address, wallet_type, status, username):
        wallet = WalletModel(address=wallet_address, type=wallet_type, status=status)
        self._register_wallet(wallet, username)
        return wallet.to_response()

    def remove_user_wallet(self, username):
        self.wallet_repo.remove_user_wallet(username)

    def get_wallet_details(self, username):
        """ Method to get wallet details for a given username. """
        logger.info(f"Fetching wallet details for {username}")
        wallet_data = self.wallet_repo.get_wallet_data_by_username(username)

        wallets = []
        for user_wallet, wallet in wallet_data:
            new_wallet = wallet.to_response()
            if wallet.encrypted_key is not None:
                new_wallet['private_key'] = self._decrypt_key(wallet.encrypted_key)
            new_wallet["is_default"] = user_wallet.is_default
            wallets.append(new_wallet)

        logger.info(f"Fetched {len(wallets)} wallets for username: {username}")
        wallet_response = {"username": username, "wallets": wallets}
        return wallet_response

    def set_default_wallet(self, username, address):
        self.wallet_repo.set_default_wallet(username=username, address=address)

    def _encrypt_key(self, private_key: str) -> str:
        key_in_bytes = bytes.fromhex(private_key)
        encrypted_key = self.fernet.encrypt(key_in_bytes)
        return encrypted_key.hex()

    def _decrypt_key(self, encrypted_key: str) -> str:
        encrypted_key_in_bytes = bytes.fromhex(encrypted_key)
        decrypted_key = self.fernet.decrypt(encrypted_key_in_bytes)
        return decrypted_key.hex()


