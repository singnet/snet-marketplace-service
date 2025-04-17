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
    ASSET_BUCKET: str = Field(default=config.AWS["S3"]["ASSET_BUCKET"])
    ASSET_DIR: str = Field(default=config.AWS["S3"]["ASSET_DIR"])
    UPLOAD_BUCKET: UploadBucketConfig = Field(default_factory=UploadBucketConfig)
    ASSET_COMPONENT_BUCKET_NAME: str = Field(default=config.AWS["S3"]["ASSET_COMPONENT_BUCKET_NAME"])
    ALLOWED_HERO_IMAGE_FORMATS: list[str] = Field(default=config.AWS["S3"]["ALLOWED_HERO_IMAGE_FORMATS"])


class AWSConfig(BaseModel):
    ALLOWED_ORIGIN: list[str] = Field(default=config.AWS["ALLOWED_ORIGIN"])
    REGION_NAME: str = Field(default=config.AWS["REGION_NAME"])
    S3: S3Config = Field(default_factory=S3Config)


class LambdaARNConfig(BaseModel):
    NOTIFICATION_ARN: str = Field(default=config.LAMBDA_ARN["NOTIFICATION_ARN"])
    VERIFICATION_ARN: dict = Field(default=config.LAMBDA_ARN["VERIFICATION_ARN"])
    SERVICE_CURATE_ARN: str = Field(default=config.LAMBDA_ARN["SERVICE_CURATE_ARN"])
    DEMO_COMPONENT: dict = Field(default=config.LAMBDA_ARN["DEMO_COMPONENT"])
    MANAGE_PROTO_COMPILATION_LAMBDA_ARN: str = Field(default=config.LAMBDA_ARN["MANAGE_PROTO_COMPILATION_LAMBDA_ARN"])
    PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT: str = Field(default=config.LAMBDA_ARN["PUBLISH_OFFCHAIN_ATTRIBUTES_ENDPOINT"])
    GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT: str = Field(default=config.LAMBDA_ARN["GET_SERVICE_FOR_GIVEN_ORG_ENDPOINT"])


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
    db: DBConfig = Field(default_factory=DBConfig)
    slack: SlackHookConfig = Field(default_factory=SlackHookConfig)
    ipfs: IPFSConfig = Field(default_factory=IPFSConfig)
    emails: EmailsConfig = Field(default_factory=EmailsConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    lambda_arn: LambdaARNConfig = Field(default_factory=LambdaARNConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


settings = Settings()
