import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from backend.dependencies import (
    API_BASE_URL,
    get_current_customer,
    get_customer_service,
    get_base_url,
    require_customer_ownership,
)
from backend.schemas.Users import CustomerResponse, MerchantResponse
from backend.schemas.Users.Customer import CustomerUpdate
from backend.service.customer_service import CustomerService

router = APIRouter(prefix=f"{get_base_url}/customer", tags=["Customer"])

@router.get("/", response_model=CustomerResponse)
def get_customers(current_customer: CustomerResponse = Depends(get_current_customer)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the active customer's profile.

    Args / Parameters:
        current_customer (CustomerResponse): Customer resolved from the active session.

    Returns:
        CustomerResponse: The active customer's public profile.

    Constraints / Notes:
        Requires an active customer session.
    """
    return current_customer

@router.get('/stores', status_code=status.HTTP_200_OK, response_model=list[dict])
def get_stores(service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve a list of all registered merchant store profiles.

    Args / Parameters:
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        list[dict]: List of merchant store summary dictionaries.

    Constraints / Notes:
        Queries merchant store records using the API base URL.
    """
    try:
        return service.get_stores(API_BASE_URL)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve stores from the merchant service.",
        ) from error

@router.get('/stores/{store_name}', status_code=status.HTTP_200_OK, response_model=MerchantResponse)
def get_merchant_by_store(store_name: str, service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve merchant profile details for a given store name.

    Args / Parameters:
        store_name (str): The unique store name to search for.
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        MerchantResponse: Matching merchant profile schema.

    Constraints / Notes:
        Raises HTTP 404 if the store name does not exist.
    """
    try:
        merchant = service.get_merchant(store_name)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve the requested store.",
        ) from error
    if merchant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return merchant

@router.get('/stores/{store_name}/all_products', status_code=status.HTTP_200_OK, response_model=list[dict])
def get_store_products(store_name: str, service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve all inventory products associated with a specific store.

    Args / Parameters:
        store_name (str): The unique store name to look up.
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        list[dict]: List of product inventory dictionaries belonging to the store.

    Constraints / Notes:
        Returns empty list if the store exists but has no registered products.
    """
    try:
        return service.get_store_products(store_name)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve products from the merchant service.",
        ) from error

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_by_id(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve a single customer by their unique ID string.

    Args / Parameters:
        customer_id (str): The customer ID string (UUID or legacy ID) from URL path parameter.
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        dict: The matching customer record.

    Constraints / Notes:
        Raises HTTP 404 Exception if no customer matching the given ID is found.
    """
    customer = service.get_user_by_id(str(current_customer.id))
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

@router.patch("/{customer_id}", response_model=CustomerResponse)
def edit_customer_account(
    customer_id: str,
    payload: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
) -> CustomerResponse:
    """Update the active customer's editable profile fields.

    Args:
        customer_id: Customer ID from the route.
        payload: Validated partial profile update.
        service: Customer persistence service.
        current_customer: Active customer resolved and checked against the route ID.

    Returns:
        The updated customer profile.

    Constraints / Notes:
        Returns 403 for another customer's ID and 404 if the account does not exist.
    """
    customer = service.get_user_by_id(str(current_customer.id))
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    updated_customer = service.update(str(current_customer.id), payload)
    if updated_customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerResponse(**updated_customer)
