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
    # adding this allows for referencing variables as attributes, e.g., url.short_code, instead of dict - url["short_code"]

class URLUpdate(BaseModel):
    original_url: HttpUrl

class URLStats(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    updated_at: datetime
    access_count: int

    model_config = {"from_attributes": True}
