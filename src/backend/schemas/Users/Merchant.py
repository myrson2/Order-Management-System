import uuid
from pydantic import Field, field_validator, BaseModel
from uuid import UUID, uuid4
from backend.schemas.Users.User import EnumType, UserCreate, UserResponse


class Merchant(UserCreate):
    user_type: EnumType = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(default_factory=uuid4)

    @field_validator("user_type")
    @classmethod
    def validate_merchant_user_type(cls, value: EnumType | None) -> EnumType:
        """Require merchant records to use the merchant enum value.

        Args:
            value: User type supplied for the merchant.

        Returns:
            The validated merchant enum value.

        Raises:
            ValueError: If the value is not the merchant enum value.
        """
        if value is not EnumType.MERCHANT:
            raise ValueError("Merchant user_type must be MERCHANT")
        return EnumType.MERCHANT

class MerchantCreate(Merchant):
    pass

class MerchantResponse(UserResponse):
    user_type: EnumType = EnumType.MERCHANT
    store_name: str = Field(..., min_length=1, max_length=50)
    tax_id: UUID = Field(default_factory=uuid4)

    @field_validator("user_type")
    @classmethod
    def validate_merchant_user_type(cls, value: EnumType | None) -> EnumType:
        """Require merchant responses to use the merchant enum value.

        Args:
            value: User type supplied for the merchant response.

        Returns:
            The validated merchant enum value.

        Raises:
            ValueError: If the value is not the merchant enum value.
        """
        if value is not EnumType.MERCHANT:
            raise ValueError("Merchant user_type must be MERCHANT")
        return EnumType.MERCHANT

class MerchantUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    store_name: str | None = Field(default=None, max_length=50)

    @field_validator("first_name", "last_name", "store_name", mode="before")
    @classmethod
    def blank_string_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

