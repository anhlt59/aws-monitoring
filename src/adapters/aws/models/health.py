from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from src.adapters.aws.models.base import Region

EventTypeCategory = Literal["issue", "accountNotification", "scheduledChange", "investigation"]
StatusCode = Literal["open", "closed", "upcoming"]
EventScopeCode = Literal["PUBLIC", "ACCOUNT_SPECIFIC", "NONE"]


class HealthEventDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    service: str
    status_code: StatusCode = Field(alias="statusCode")
    start_time: str = Field(alias="startTime")
    last_update_time: str = Field(alias="lastUpdatedTime")

    event_arn: str = Field(alias="eventArn")
    event_type_code: str = Field(alias="eventTypeCode")
    event_type_category: EventTypeCategory = Field(alias="eventTypeCategory")
    event_scope_code: EventScopeCode = Field(alias="eventScopeCode")
    event_region: Region = Field(alias="eventRegion")
    event_description: list[dict] | None = Field(alias="eventDescription", default=None)

    affected_entities: list[dict] | None = Field(alias="affectedEntities", default=None)
    affected_account: str | None = Field(alias="affectedAccount", default=None)


class HealthEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    detail_type: str = Field(alias="detail-type")
    source: str
    account: str
    time: str
    region: Region
    resources: list[Any] | None = None
    detail: HealthEventDetail
