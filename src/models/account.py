# Account data model
from typing import List, Union

from pydantic import BaseModel, Field
from uuid_utils import uuid7


class Account(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid7()))
    project_id: str
    name: str
    active_regions: List[str]
    assume_role_arn: str


class AccountCreateDTO(BaseModel):
    project_id: str
    name: str
    active_regions: List[str]
    assume_role_arn: str


class AccountUpdateDTO(BaseModel):
    name: Union[str, None] = None
    active_regions: Union[List[str], None] = None
    assume_role_arn: Union[str, None] = None
