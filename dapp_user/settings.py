from dapp_user import config
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class LambdaARNConfig(BaseModel):
    delete_user_wallet_arn: str

class Settings(BaseSettings):
    stage: str
    db: DBConfig
    slack: SlackHookConfig
    aws: AWSConfig
    lambda_arn: LambdaARNConfig

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


settings = Settings(
    stage=config.STAGE,
    db=DBConfig(**config.DB_CONFIG),
    slack=SlackHookConfig(**config.SLACK_HOOK),
    aws=AWSConfig(**config.AWS),
    lambda_arn=LambdaARNConfig(**config.LAMBDA_ARN),
)
