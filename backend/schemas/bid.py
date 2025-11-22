from datetime import datetime

from pydantic import BaseModel


class BidBase(BaseModel):
    amount: float


class BidCreate(BidBase):
    artwork_id: int


class BidResponse(BidBase):
    id: int
    artwork_id: int
    bidder_id: int
    created_at: datetime
    is_winning: bool

    class Config:
        from_attributes = True
