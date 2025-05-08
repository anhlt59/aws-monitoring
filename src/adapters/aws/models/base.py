from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel

# fmt: off
Region = Literal["us-east-1", "us-east-2", "us-west-1", "us-west-2", "af-south-1", "ap-east-1", "ap-south-1", "ap-northeast-3", "ap-northeast-2", "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ca-central-1", "cn-north-1", "cn-northwest-1", "eu-central-1", "eu-west-1", "eu-west-2", "eu-south-1", "eu-west-3", "eu-north-1", "me-south-1", "sa-east-1"]
# fmt: on


class Credentials(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: str | None = None
    aws_expiration: datetime | None = None
    aws_arn: str | None = None

    def is_expired(self):
        if self.aws_expiration is None:
            return False
        return self.aws_expiration < datetime.now(timezone.utc)


class Identity(BaseModel):
    user_id: str
    account: str
    arn: str


class Profile(BaseModel):
    name: str
    region: Region
    credentials: Credentials
    identity: Identity | None = None
