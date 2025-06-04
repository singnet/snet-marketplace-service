from typing import Literal
from registry import config
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


class IPFSConfig(BaseModel):
    URL: str = Field(default=config.IPFS_URL["url"])
    PORT: str = Field(default=config.IPFS_URL["port"])


class EmailsConfig(BaseModel):
    PUBLISHER_PORTAl_DAPP_URL: str = Field(default=config.EMAILS["PUBLISHER_PORTAL_DAPP_URL"])
    PUBLISHER_PORTAL_SUPPORT_MAIL: str = Field(default=config.EMAILS["PUBLISHER_PORTAL_SUPPORT_MAIL"])
    ORG_APPROVERS_DLIST: str = Field(default=config.EMAILS["ORG_APPROVERS_DLIST"])
    SERVICE_APPROVERS_DLIST: str = Field(default=config.EMAILS["SERVICE_APPROVERS_DLIST"])


class UploadBucketConfig(BaseModel):
    ORG_BUCKET: str = Field(default=config.AWS["S3"]["UPLOAD_BUCKET"]["ORG_BUCKET"])


class S3Config(BaseModel):
    ASSETS_BUCKET: str = Field(default=config.AWS["S3"]["ASSETS_BUCKET"])
    ASSET_DIR: str = Field(default=config.AWS["S3"]["ASSET_DIR"])
    UPLOAD_BUCKET: UploadBucketConfig = Field(default_factory=UploadBucketConfig)
    ASSET_COMPONENT_BUCKET_NAME: str = Field(default=config.AWS["S3"]["ASSET_COMPONENT_BUCKET_NAME"])
    ALLOWED_HERO_IMAGE_FORMATS: list[str] = Field(default=config.AWS["S3"]["ALLOWED_HERO_IMAGE_FORMATS"])


class AWSConfig(BaseModel):
    ALLOWED_ORIGIN: list[str] = Field(default=config.AWS["ALLOWED_ORIGIN"])
    REGION_NAME: str = Field(default=config.AWS["REGION_NAME"])
    S3: S3Config = Field(default_factory=S3Config)


class DemoComponentConfig(BaseModel):
    CODE_BUILD_NAME: str = Field(default=config.LAMBDA_ARN["DEMO_COMPONENT"]["CODE_BUILD_NAME"])
    UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN: str = Field(
        default=config.LAMBDA_ARN["DEMO_COMPONENT"]["UPDATE_DEMO_COMPONENT_BUILD_STATUS_LAMBDA_ARN"]
    )


class PublishOffchainAttributesConfig(BaseModel):
    FET: str = Field(default=config.LAMBDA_ARN["PUBLISH_OFFCHAIN_ATTRIBUTES_LAMBDAS"]["FET"])
    AGIX: str = Field(default=config.LAMBDA_ARN["PUBLISH_OFFCHAIN_ATTRIBUTES_LAMBDAS"]["AGIX"])

    def __getitem__(self, token_name: Literal["FET", "AGIX"]) -> str:
        return getattr(self, token_name)


class GetServiceForGiverOrgLambdas(BaseModel):
    FET: str = Field(default=config.LAMBDA_ARN["GET_SERVICE_FOR_GIVEN_ORG_LAMBDAS"]["FET"])
    AGIX: str = Field(default=config.LAMBDA_ARN["GET_SERVICE_FOR_GIVEN_ORG_LAMBDAS"]["AGIX"])

    def __getitem__(self, token_name: Literal["FET", "AGIX"]) -> str:
        return getattr(self, token_name)


class LambdaARNConfig(BaseModel):
    NOTIFICATION_ARN: str = Field(default=config.LAMBDA_ARN["NOTIFICATION_ARN"])
    VERIFICATION_ARN: dict = Field(default=config.LAMBDA_ARN["VERIFICATION_ARN"])
    SERVICE_CURATE_ARN: str = Field(default=config.LAMBDA_ARN["SERVICE_CURATE_ARN"])
    DEMO_COMPONENT: DemoComponentConfig = Field(
        default_factory=DemoComponentConfig
    )
    MANAGE_PROTO_COMPILATION_LAMBDA_ARN: str = Field(default=config.LAMBDA_ARN["MANAGE_PROTO_COMPILATION_LAMBDA_ARN"])
    PUBLISH_OFFCHAIN_ATTRIBUTES_ARN: PublishOffchainAttributesConfig = Field(
        default_factory=PublishOffchainAttributesConfig
    )
    GET_SERVICE_FOR_GIVEN_ORG_LAMBDAS: GetServiceForGiverOrgLambdas = Field(
        default_factory=GetServiceForGiverOrgLambdas
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
    stage: str = Field(default=config.STAGE)
    token_name: str = Field(default=config.TOKEN_NAME)
    db: DBConfig = Field(default_factory=DBConfig)
    slack: SlackHookConfig = Field(default_factory=SlackHookConfig)
    ipfs: IPFSConfig = Field(default_factory=IPFSConfig)
    emails: EmailsConfig = Field(default_factory=EmailsConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    lambda_arn: LambdaARNConfig = Field(default_factory=LambdaARNConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


settings = Settings()
