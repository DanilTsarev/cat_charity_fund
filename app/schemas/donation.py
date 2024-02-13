from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt


class DonationBase(BaseModel):
    full_amount: PositiveInt


class DonationCreate(DonationBase):
    comment: Optional[str]


class DonationDB(DonationCreate):
    id: int
    create_date: datetime


class DonationDBAdmin(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
