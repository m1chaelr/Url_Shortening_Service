from pydantic import BaseModel, HttpUrl
from datetime import datetime

class URLCreate(BaseModel):
    '''Request schema - what the client is allowed to send.'''
    original_url: HttpUrl

class URLResponse(BaseModel):
    '''Response schema - what the api promises to return.'''
    id: int
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    updated_at: datetime
    access_count: int

    model_config = {"from_attributes": True}
