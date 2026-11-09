from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator

class PanelOut(BaseModel):
    id: int; code: str; name: str; x: float; y: float; width: float; height: float
    model_config = {"from_attributes": True}

class ReservationCreate(BaseModel):
    panel_id: int
    project_name: str = Field(min_length=1, max_length=150)
    purchase_order: str | None = Field(default=None, max_length=80)
    requester: str = Field(min_length=1, max_length=80)
    start_date: date
    end_date: date
    note: str | None = Field(default=None, max_length=1000)
    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("종료일은 시작일보다 빠를 수 없습니다.")
        return self

class ReservationOut(BaseModel):
    id: int; panel_id: int; panel_code: str; project_name: str
    purchase_order: str | None; requester: str; start_date: date; end_date: date
    note: str | None; created_at: datetime
