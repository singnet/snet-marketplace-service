from typing import Dict
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from signer import config


class DBConfig(BaseModel):
    driver: str
    host: str
    port: int
    user: str
    password: str
    name: str


class SlackHookConfig(BaseModel):
    hostname: str
    path: str


class AWSConfig(BaseModel):
    region_name: str


class SignerConfig(BaseModel):
    key: str
    address: str
    expiration_block_count: int


class LambdaARNConfig(BaseModel):
    get_service_details_arn: str


class NetworkDetail(BaseModel):
    name: str
    http_provider: str
    ws_provider: str
    contract_base_path: str


class NetworkConfig(BaseModel):
    id: int
    networks: Dict[int, NetworkDetail]


class Settings(BaseSettings):
    stage: str
    token_name: str
    db: DBConfig
    slack: SlackHookConfig
    aws: AWSConfig
    lambda_arn: LambdaARNConfig
    network: NetworkConfig
    signer: SignerConfig

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


settings = Settings(
    stage=config.STAGE,
    token_name=config.TOKEN_NAME,
    db=DBConfig(**config.DB_CONFIG),
    slack=SlackHookConfig(**config.SLACK_HOOK),
    aws=AWSConfig(**config.AWS),
    lambda_arn=LambdaARNConfig(**config.LAMBDA_ARN),
    network=NetworkConfig(
        id=config.NETWORK_ID, networks={k: NetworkDetail(**v) for k, v in config.NETWORKS.items()}
    ),
    signer=SignerConfig(**config.SIGNER),
)
