from fastapi import APIRouter, Depends, HTTPException, status
from backend.dependencies import get_customer_service, API_BASE_URL
from backend.schemas.Users import Customer, MerchantResponse
from backend.service.customer_service import CustomerService
from backend.dependencies import get_base_url

router = APIRouter(prefix=f"{get_base_url}/customer", tags=["Customer"])

@router.get("/")
def get_customers(service: CustomerService = Depends(get_customer_service)):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the list of all registered customers.

    Args / Parameters:
        service (CustomerService): Injected CustomerService dependency.

    Returns:
        list[dict]: List of customer dictionaries.

    Constraints / Notes:
        Returns cached list of customers stored in memory / customer.json.
    """
    return service.get_all()

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
    return service.get_stores(API_BASE_URL)

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
    return service.get_merchant(store_name)

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
    return service.get_store_products(store_name)

# @router.get('/stores/{store_name/product/{product_id}', status_code=status.HTTP_200_OK, response_model=MerchantResponse)
# def get_product_by_id(store_name: str, product_id: str, service: CustomerService = Depends(get_customer_service)):
#     pass

@router.get("/{customer_id}")
def get_customer_by_id(customer_id: str, service: CustomerService = Depends(get_customer_service)):
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
    customer = service.get_user_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

# @router.patch("/{customer_id}", status_code=status.HTTP_200_OK)
# def edit_customer_account(customer_id: str, payload: CustomerUpdate, service: CustomerService = Depends(get_customer_service)):
#     update_data = service.update_customer(customer_id, payload)
#     if not update_data:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
#     return update_data











