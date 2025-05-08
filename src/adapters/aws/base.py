import boto3

from src.adapters.aws.models.base import Credentials, Profile, Region
from src.common.configs import AWS_DEFAULT_PROFILE, AWS_REGIONS
from src.common.meta import SingletonMeta
from src.common.processes import execute_command


class SessionService(metaclass=SingletonMeta):
    profile: Profile
    session: boto3.Session

    def __init__(self, profile_name: str = AWS_DEFAULT_PROFILE, region: Region | None = None):
        self.switch_profile(profile_name)
        if region:
            self.change_region(region)

    def client(self, *args, **kwargs) -> boto3.client:
        return self.session.client(*args, **kwargs)

    def resource(self, *args, **kwargs) -> boto3.resource:
        return self.session.resource(*args, **kwargs)

    def get_profile(self, profile_name: str = AWS_DEFAULT_PROFILE) -> Profile:
        session = boto3.Session(profile_name=profile_name)
        credentials = session.get_credentials()
        return Profile(
            name=session.profile_name,
            region=session.region_name,
            credentials=Credentials(
                aws_access_key_id=credentials.access_key,
                aws_secret_access_key=credentials.secret_key,
                aws_session_token=credentials.token,
            ),
        )

    def switch_profile(self, profile_name: str):
        self.profile = self.get_profile(profile_name)
        self.session = boto3.Session(profile_name=profile_name)

    def change_region(self, region: Region):
        if region not in AWS_REGIONS:
            raise ValueError(f"Region {region} is not available")
        self.profile.region = region
        self.session = boto3.Session(profile_name=self.profile.name, region_name=region)

    def set_credentials(self, credentials: Credentials) -> Profile:
        self.profile.credentials = credentials
        self.session = boto3.Session(
            aws_access_key_id=credentials.aws_access_key_id,
            aws_secret_access_key=credentials.aws_secret_access_key,
            aws_session_token=credentials.aws_session_token,
            region_name=self.profile.region,
        )
        return self.profile

    def assume_role(self, arn: str) -> Credentials:
        response = self.session.client("sts").assume_role(RoleArn=arn, RoleSessionName="session")
        if credentials := response.get("Credentials"):
            return Credentials(
                aws_arn=arn,
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                aws_expiration=credentials["Expiration"],
            )
        else:
            raise Exception(f"Failed to assume role {arn}")

    def get_session_token(self, anr: str, mfa_token: str) -> Credentials:
        if not anr or not mfa_token:
            raise ValueError("SerialNumber and MFA code are required")
        session = boto3.Session(profile_name=self.profile.name)
        response = session.client("sts").get_session_token(SerialNumber=anr, TokenCode=mfa_token)
        if credentials := response.get("Credentials"):
            return Credentials(
                aws_arn=anr,
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
                aws_expiration=credentials["Expiration"],
            )
        else:
            raise Exception(f"Failed to assume role {anr}")

    def store_aws_config_file(self, profile: Profile, name: str = AWS_DEFAULT_PROFILE):
        aws_access_key_id = profile.credentials.aws_access_key_id
        aws_secret_access_key = profile.credentials.aws_secret_access_key
        aws_session_token = profile.credentials.aws_session_token
        execute_command(f"aws configure set output json --profile {name}")
        execute_command(f"aws configure set region {profile.region} --profile {name}")
        execute_command(f"aws configure set aws_access_key_id {aws_access_key_id} --profile {name}")
        execute_command(f"aws configure set aws_secret_access_key {aws_secret_access_key} --profile {name}")
        if aws_session_token:
            execute_command(f"aws configure set aws_session_token {aws_session_token} --profile {name}")


class AwsService(metaclass=SingletonMeta):
    session: SessionService

    def __init__(self, session: SessionService, *args, **kwargs):
        self.session = session
