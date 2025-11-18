from datetime import datetime

from pydantic import BaseModel, field_validator


class BidBase(BaseModel):
    amount: float


class BidCreate(BidBase):
    artwork_id: int

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Bid amount must be non-negative")
        return v


class BidResponse(BidBase):
    id: int
    artwork_id: int
    bidder_id: int
    bid_time: datetime
    is_winning: bool

    class Config:
        from_attributes = True
