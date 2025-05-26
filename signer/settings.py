from signer import config
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseModel):
    DRIVER: str = Field(default=config.DB_CONFIG["driver"])
    HOST: str = Field(default=config.DB_CONFIG["host"])
    PORT: int = Field(default=config.DB_CONFIG["port"])
    USER: str = Field(default=config.DB_CONFIG["user"])
    PASSWORD: str = Field(default=config.DB_CONFIG["password"])
    NAME: str = Field(default=config.DB_CONFIG["name"])


class SlackHookConfig(BaseModel):
    HOSTNAME: str = Field(default=config.SLACK_HOOK["hostname"])
    PATH: str = Field(default=config.SLACK_HOOK["path"])


class AWSConfig(BaseModel):
    REGION_NAME: str = Field(default=config.AWS["REGION_NAME"])


class SignerConfig(BaseModel):
    KEY: str = Field(default=config.SIGNER["KEY"])
    ADDRESS: str = Field(default=config.SIGNER["ADDRESS"])


class LambdaARNConfig(BaseModel):
    get_service_deatails_arn: str = Field(
        default=config.LAMBDA_ARN["GET_SERVICE_DETAILS_FOR_GIVEN_ORG_ID_AND_SERVICE_ID_ARN"]
    )
    metering_arn: str = Field(
        default=config.LAMBDA_ARN["METERING_ARN"]
    )
    prefix_free_call: str = Field(
        default=config.LAMBDA_ARN["PREFIX_FREE_CALL"]
    )

class NetworkDetail(BaseModel):
    name: str
    http_provider: str
    ws_provider: str
    contract_base_path: str


class NetworkConfig(BaseModel):
    networks: dict[int, NetworkDetail] = Field(
        default={k: NetworkDetail(**v) for k, v in config.NETWORKS.items()}
    )
    id: int = Field(default=config.NETWORK_ID)



class Settings(BaseSettings):
    stage: str = Field(default="dev")
    token_name: str = Field(default="FET")
    db: DBConfig = Field(default_factory=DBConfig)
    slack: SlackHookConfig = Field(default_factory=SlackHookConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    lambda_arn: LambdaARNConfig = Field(default_factory=LambdaARNConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    signer: SignerConfig = Field(default_factory=SignerConfig)



    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


settings = Settings()
