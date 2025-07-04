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
    cognito_pool: str


class DeleteUserWallet(BaseModel):
    fet: str
    agix: str


class UpdateServiceRating(BaseModel):
    fet: str
    agix: str


class LambdaARNConfig(BaseModel):
    delete_user_wallet_arn: DeleteUserWallet
    update_service_rating_arn: UpdateServiceRating


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
    lambda_arn=LambdaARNConfig(
        delete_user_wallet_arn=DeleteUserWallet(**config.LAMBDA_ARN["delete_user_wallet_arn"]),
        update_service_rating_arn=UpdateServiceRating(
            **config.LAMBDA_ARN["update_service_rating_arn"]
        ),
    ),
)
