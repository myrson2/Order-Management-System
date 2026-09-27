from typing import Literal
from backend.schemas.Users.User import EnumType, UserCreate, UserResponse
from pydantic import Field

class Customer(UserCreate):
    user_type: Literal[EnumType.CUSTOMER] = EnumType.CUSTOMER
    rewards: float = Field(default=0)

class CustomerCreate(Customer):
    pass

class CustomerResponse(UserResponse):
    user_type: Literal[EnumType.CUSTOMER] = EnumType.CUSTOMER
    rewards: float = Field(default=0)