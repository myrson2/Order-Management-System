from backend.schemas.Users.User import EnumType, UserCreate, UserResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class Customer(UserCreate):
    user_type: EnumType =  EnumType.CUSTOMER
    rewards: float = Field(default=0)

    @field_validator("user_type")
    @classmethod
    def validate_customer_user_type(cls, value: EnumType | None) -> EnumType:
        """Require customer records to use the customer enum value.

        Args:
            value: User type supplied for the customer.

        Returns:
            The validated customer enum value.

        Raises:
            ValueError: If the value is not the customer enum value.
        """
        if value is not EnumType.CUSTOMER:
            raise ValueError("Customer user_type must be CUSTOMER")
        return EnumType.CUSTOMER

class CustomerCreate(Customer):
    pass

class CustomerResponse(UserResponse):
    user_type: EnumType = EnumType.CUSTOMER
    rewards: float = Field(default=0)

    @field_validator("user_type")
    @classmethod
    def validate_customer_user_type(cls, value: EnumType | None) -> EnumType:
        """Require customer responses to use the customer enum value.

        Args:
            value: User type supplied for the customer response.

        Returns:
            The validated customer enum value.

        Raises:
            ValueError: If the value is not the customer enum value.
        """
        if value is not EnumType.CUSTOMER:
            raise ValueError("Customer user_type must be CUSTOMER")
        return EnumType.CUSTOMER

class CustomerUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=11)

    @field_validator("email")
    @classmethod
    def validate_update_email(cls, value: EmailStr | None) -> EmailStr | None:
        """Restrict an updated email address to the customer email domain.

        Args:
            value: Optional email address supplied in the update.

        Returns:
            The validated email address, or None when omitted.

        Constraints / Notes:
            Non-empty values must end with '@gmail.com'.
        """
        if value is not None and not str(value).endswith("@gmail.com"):
            raise ValueError("Email address must end with @gmail.com")
        return value

    @field_validator("phone")
    @classmethod
    def validate_update_phone(cls, value: str | None) -> str | None:
        """Validate an optional customer phone-number update.

        Args:
            value: Optional phone number supplied in the update.

        Returns:
            The validated phone number, or None when omitted.

        Constraints / Notes:
            Non-empty values must be 11 digits and start with '09'.
        """
        if value is not None and (not value.isdigit() or len(value) != 11 or not value.startswith("09")):
            raise ValueError("Phone number must start with 09 and be 11 digits long")
        return value