from datetime import datetime
from typing import Self

from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import uuid4, UUID
from enum import Enum

class EnumType(str, Enum):
    CUSTOMER = 'customer'
    MERCHANT = 'merchant'

class ActiveStatus(str, Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr
    user_type: EnumType
    phone: str = Field(max_length=11)
    created_at: datetime = Field(default_factory=datetime.now)
    active_status: ActiveStatus = ActiveStatus.OFFLINE

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Description / Purpose:
            Validates that the provided email address uses a valid @gmail.com domain.

        Args / Parameters:
            value (str): The email address input string.

        Returns:
            str: The validated email address string.

        Constraints / Notes:
            Raises ValueError if the email string does not end with '@gmail.com'.
        """
        if value.endswith('@gmail.com'):
            return value
        else:
            raise ValueError('Email address must end with @gmail.com')

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """
        Description / Purpose:
            Validates that the phone number starts with '09' or is exactly 11 digits long.

        Args / Parameters:
            value (str): The phone number input string.

        Returns:
            str: The validated phone number string.

        Constraints / Notes:
            Raises ValueError if the phone number does not start with '09' or is not 11 digits.
        """
        if value.startswith('09') or len(value) == 11:
            return value
        else:
            raise ValueError('Phone number must start with 09 and be 11 digits long')

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """
        Description / Purpose:
            Instantiates a User model from a dictionary payload.

        Args / Parameters:
            data (dict): Dictionary containing user attributes.

        Returns:
            User: Validated User model instance.

        Constraints / Notes:
            Unpacks keys as keyword arguments into model initialization.
        """
        return cls(**data)  
    
    def to_dict(self) -> dict:
        """
        Description / Purpose:
            Serializes the User model into a JSON-compatible dictionary.

        Args / Parameters:
            None.

        Returns:
            dict: Dictionary with UUIDs, datetime, and complex objects serialized as JSON strings.

        Constraints / Notes:
            Uses mode='json' to ensure output is safe for file storage and HTTP network payloads.
        """
        return self.model_dump(mode='json')

    def online(self) -> None:
        """
        Description / Purpose:
            Mutates the user's active status state to ONLINE.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Directly updates self.active_status attribute using ActiveStatus.ONLINE enum.
        """
        self.active_status = ActiveStatus.ONLINE

    def offline(self) -> None:
        """
        Description / Purpose:
            Mutates the user's active status state to OFFLINE.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Directly updates self.active_status attribute using ActiveStatus.OFFLINE enum.
        """
        self.active_status = ActiveStatus.OFFLINE

class UserCreate(User):
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Description / Purpose:
            Enforces strong password complexity requirements.

        Args / Parameters:
            value (str): The raw password string.

        Returns:
            str: The validated password string.

        Constraints / Notes:
            Must contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character.
        """
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter")

        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number")

        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain a special character")

        return value

class UserLogin(BaseModel):
    email: EmailStr

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Description / Purpose:
            Validates that the provided email address uses a valid @gmail.com domain.

        Args / Parameters:
            value (str): The email address input string.

        Returns:
            str: The validated email address string.

        Constraints / Notes:
            Raises ValueError if the email string does not end with '@gmail.com'.
        """
        if value.endswith('@gmail.com'):
            return value
        else:
            raise ValueError('Email address must end with @gmail.com')

    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Description / Purpose:
            Enforces strong password complexity requirements.

        Args / Parameters:
            value (str): The raw password string.

        Returns:
            str: The validated password string.

        Constraints / Notes:
            Must contain at least 1 uppercase letter, 1 lowercase letter, 1 digit, and 1 special character.
        """
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain an uppercase letter")

        if not any(char.islower() for char in value):
            raise ValueError("Password must contain a lowercase letter")

        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain a number")

        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain a special character")

        return value

    def to_dict(self) -> dict:
        """
        Description / Purpose:
            Serializes UserLogin model attributes into a JSON-compatible dictionary.

        Args / Parameters:
            None.

        Returns:
            dict: Dictionary representation of login credentials.

        Constraints / Notes:
            Uses mode='json' serialization.
        """
        return self.model_dump(mode="json")

class UserResponse(User):
    """
    Public response schema for authenticated user entities.
    Inherits all non-sensitive identity and status attributes from User.
    """
    pass