from pydantic import BaseModel
from datetime import datetime

class BidBase(BaseModel):
    amount: float

class BidCreate(BidBase):
    artwork_id: int

class BidResponse(BidBase):
    id: int
    artwork_id: int
    bidder_id: int
    bid_time: datetime
    is_winning: bool

    class Config:
        from_attributes = True