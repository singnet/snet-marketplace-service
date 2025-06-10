from utility import config
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class SlackHookConfig(BaseModel):
    HOSTNAME: str = Field(default=config.SLACK_HOOK["hostname"])
    PATH: str = Field(default=config.SLACK_HOOK["path"])
    SLACK_FEEDBACK_HOOK: dict[str, str] = Field(default=config.SLACK_FEEDBACK_HOOK)

class NetworkDetail(BaseModel):
    name: str
    http_provider: str
    ws_provider: str

class NetworkConfig(BaseModel):
    networks: dict[int, NetworkDetail] = Field(
        default={k: NetworkDetail(**v) for k, v in config.NETWORKS.items()}
    )
    id: int = Field(default=config.NETWORK_ID)

class S3Config(BaseModel):
    FEEDBACK_BUCKET: str = Field(default = config.UPLOAD_BUCKET["FEEDBACK_BUCKET"])
    ORG_BUCKET: str = Field(default = config.UPLOAD_BUCKET["ORG_BUCKET"])

class AWSConfig(BaseModel):
    REGION_NAME: str = Field(default=config.REGION_NAME)
    S3: S3Config = Field(default_factory=S3Config)

class FilesConfig(BaseModel):
    FILE_EXTENSION: dict[str, str] = Field(default = config.FILE_EXTENSION)
    ALLOWED_CONTENT_TYPE: list[str] = Field(default = config.ALLOWED_CONTENT_TYPE)

class LambdaARNConfig(BaseModel):
    NODEJS_PROTO_LAMBDA_ARN: str = Field(default=config.NODEJS_PROTO_LAMBDA_ARN)
    PYTHON_PROTO_LAMBDA_ARN: dict = Field(default=config.PYTHON_PROTO_LAMBDA_ARN)

class CompileProtoConfig(BaseModel):
    PROTO_DIRECTORY_REGEX_PATTERN: str = Field(default = config.PROTO_DIRECTORY_REGEX_PATTERN)
    SUPPORTED_ENVIRONMENT: list[str] = Field(default = config.SUPPORTED_ENVIRONMENT)
    ARN: LambdaARNConfig = Field(default_factory=LambdaARNConfig)

class Settings(BaseSettings):
    slack: SlackHookConfig = Field(default_factory=SlackHookConfig)
    aws: AWSConfig = Field(default_factory=AWSConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    files: FilesConfig = Field(default_factory=FilesConfig)
    compile_proto: CompileProtoConfig = Field(default_factory=CompileProtoConfig)

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


settings = Settings()