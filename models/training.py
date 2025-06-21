from pydantic import BaseModel, validator
from datetime import datetime, time, date

class Training(BaseModel):
    id: int | None = None
    category: str
    description: str
    date: date
    start_time: time
    end_time: time

    @validator('end_time')
    def check_end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("L’heure de fin doit être après celle de début")
        return v

