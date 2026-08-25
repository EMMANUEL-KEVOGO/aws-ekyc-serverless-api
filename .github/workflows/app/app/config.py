import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE: str = os.getenv("DYNAMODB_TABLE", "ekyc-verifications-prod")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "ekyc-document-store-prod")
    COGNITO_USER_POOL_ID: str = os.getenv("COGNITO_USER_POOL_ID", "")
    COGNITO_CLIENT_ID: str = os.getenv("COGNITO_CLIENT_ID", "")

settings = Settings()
