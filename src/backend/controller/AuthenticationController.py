from fastapi import APIRouter, Depends, HTTPException, status
from backend.dependencies import AUTH_SERVICE_URL, get_auth_service, get_customer_service, get_merchant_service
from backend.schemas.Users.Customer import CustomerCreate, CustomerResponse
from backend.schemas.Users.Merchant import MerchantCreate, MerchantResponse
from backend.schemas.Users.User import UserLogin, UserResponse
from backend.service import MerchantService, CustomerService

from backend.service.authentication_service import AuthenticationService
router = APIRouter(prefix=AUTH_SERVICE_URL, tags=["Authentication"])

@router.post("/register/merchant", status_code=status.HTTP_201_CREATED, response_model=MerchantResponse)
def merchant_registration(merchant: MerchantCreate, service: MerchantService = Depends(get_merchant_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to register a new merchant account into storage.

    Args / Parameters:
        merchant (MerchantCreate): Validated merchant creation payload.
        service (MerchantService): Injected MerchantService dependency.

    Returns:
        MerchantResponse: Serialized merchant profile response DTO.

    Constraints / Notes:
        Serializes payload using mode='json' to prevent UUID serialization issues.
    """
    user = merchant.model_dump(mode="json")
    service.add(user)
    return MerchantResponse(**user)

@router.post("/register/customer", status_code=status.HTTP_201_CREATED, response_model=CustomerResponse)
def customer_registration(customer: CustomerCreate, service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to register a new customer account into storage.

    Args / Parameters:
        customer (CustomerCreate): Validated customer creation payload.
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        CustomerResponse: Serialized customer profile response DTO.

    Constraints / Notes:
        Serializes payload using mode='json' to prevent UUID serialization issues.
    """
    user = customer.model_dump(mode="json")
    service.add(user)
    return CustomerResponse(**user)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_login_in(user: UserLogin, service: AuthenticationService = Depends(get_auth_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to authenticate user credentials and transition active status to online.

    Args / Parameters:
        user (UserLogin): Validated login payload containing user email and password.
        service (AuthenticationService): Injected AuthenticationService singleton.

    Returns:
        UserResponse: Authenticated customer or merchant response DTO.

    Constraints / Notes:
        Raises HTTP 401 UNAUTHORIZED if matching credentials are not found in storage caches.
    """
    account = service.login(user)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.")
    return account

@router.post("/logout")
def get_logout(user: UserResponse, service: AuthenticationService = Depends(get_auth_service)):
    """
    Description / Purpose:
        HTTP POST endpoint to terminate a user session and transition active status to offline.

    Args / Parameters:
        user (UserResponse): DTO representing the active user session requesting logout.
        service (AuthenticationService): Injected AuthenticationService singleton.

    Returns:
        dict: Confirmation message payload {"message": "Successfully logged out"}.

    Constraints / Notes:
        Raises HTTP 400 BAD REQUEST if logout operation or cache update fails.
    """
    success = service.logout(user)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")
    return {"message": "Successfully logged out"}