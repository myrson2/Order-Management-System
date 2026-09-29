from backend.schemas.Users.User import EnumType, UserCreate, UserResponse
from pydantic import Field, BaseModel, field_validator

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
    pass