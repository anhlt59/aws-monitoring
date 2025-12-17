from pydantic import model_validator

from src.common.models import PaginatedInputDTO, PaginatedOutputDTO

from .models import Event


class ListEventsDTO(PaginatedInputDTO):
    start_date: int | None = None
    end_date: int | None = None
    source: str | None = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date.")
        return self


PaginatedEventsDTO = PaginatedOutputDTO[Event]
