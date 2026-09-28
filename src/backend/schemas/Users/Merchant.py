import uuid
from typing import Literal
from pydantic import Field, field_validator, BaseModel
from uuid import UUID, uuid4
from backend.schemas.Users.User import EnumType, UserCreate, UserResponse


class Merchant(UserCreate):
    user_type: Literal[EnumType.MERCHANT] = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(default_factory=uuid4)

class MerchantCreate(Merchant):
    pass

class MerchantResponse(UserResponse):
    user_type: Literal[EnumType.MERCHANT] = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(default_factory=uuid4)

class MerchantUpdate(BaseModel):
    id: UUID
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    store_name: str | None = Field(default=None, max_length=50)

    @field_validator("first_name", "last_name", "store_name", mode="before")
    @classmethod
    def blank_string_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

