from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies import get_merchant_service, get_base_url, require_merchant_ownership
from backend.schemas.Product import ProductCreate, ProductResponse, ProductUpdate
from backend.schemas.Users import Merchant
from backend.schemas.Users.Merchant import MerchantResponse, MerchantUpdate
from backend.service.merchant_services import MerchantService

router = APIRouter(prefix=f"{get_base_url}/merchant", tags=["Merchant"])

@router.get("/")
def get_users(
        service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the full list of registered merchants.

    Args / Parameters:
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        list[dict]: List of merchant dictionaries from cache / merchant.json.

    Constraints / Notes:
        Returns all records currently in memory without pagination.
    """
    return service.get_all()

@router.post("/{merchant_id}/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_a_product(
        merchant_id: str,
        prd: ProductCreate,
    service: MerchantService = Depends(get_merchant_service),
    current_merchant: MerchantResponse = Depends(require_merchant_ownership),
) -> ProductResponse:
    """
    Description / Purpose:
        HTTP POST endpoint to add a new product under a specific merchant's catalog.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        prd (ProductCreate): Validated product creation schema from request body.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        ProductResponse: Serialized ProductResponse schema representing the newly created product.

    Constraints / Notes:
        Requires the active merchant to own the route ID and verifies the path ID matches the payload.
    """
    if str(prd.merchant_id) != str(current_merchant.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL path merchant_id does not match payload merchant_id."
        )
    return service.add_product(prd)

@router.get("/products", status_code=status.HTTP_200_OK)
def get_all_products(
        service: MerchantService = Depends(get_merchant_service)
) -> list[dict]:
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve the full catalog of products across all merchants.

    Args / Parameters:
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        list[Any]: List of product dictionaries from the in-memory product cache.

    Constraints / Notes:
        Returns an empty list if no products exist in the catalog.
    """
    return service.get_all_products()

@router.delete("/{merchant_id}/products/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def delete_a_product(
    merchant_id: str,
    product_id: str,
    service: MerchantService = Depends(get_merchant_service),
    current_merchant: MerchantResponse = Depends(require_merchant_ownership),
):
    """
    Description / Purpose:
        HTTP DELETE endpoint to remove a specific product from a merchant's inventory.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        ProductResponse: Serialized ProductResponse model of the deleted product.

    Constraints / Notes:
        Requires the active merchant to own the route ID; returns 404 if the product is not found.
    """
    del_product = service.delete_product(product_id, str(current_merchant.id))
    if not del_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return del_product

@router.get("/{merchant_id}/products/{product_id}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def get_a_product_using_id(
    merchant_id: str,
    product_id: str,
    service: MerchantService = Depends(get_merchant_service)
):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve details of a specific product by its ID under a merchant catalog.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        dict: Product record dictionary matching the provided ID.

    Constraints / Notes:
        Raises HTTP 404 HTTPException if the product ID does not exist in storage.
    """
    that_product = service.get_product_by_id(product_id, merchant_id)
    if not that_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return that_product

@router.patch("/{merchant_id}/products/{product_id}/edit", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def edit_product_endpoint(
    merchant_id: str,
    product_id: str,
    product_update: ProductUpdate,
    service: MerchantService = Depends(get_merchant_service),
    current_merchant: MerchantResponse = Depends(require_merchant_ownership),
) -> ProductResponse:
    """
    Description / Purpose:
        HTTP PATCH endpoint to edit details (name, unit price, or stock quantity) of a specific merchant product.

    Args / Parameters:
        merchant_id (str): Unique merchant UUID string from URL path parameter.
        product_id (str): Unique product ID string from URL path parameter.
        product_update (ProductUpdate): Validated update schema containing modified attributes.
        service (MerchantService): Injected MerchantService singleton dependency.

    Returns:
        ProductResponse: The updated ProductResponse schema model.

    Constraints / Notes:
        Requires the active merchant to own the route ID; returns 404 if the product is not found.
    """
    updated_product = service.update_product(str(current_merchant.id), product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No product matches ID '{product_id}'."
        )
    return updated_product

@router.get('/{merchant_id}/products', status_code=status.HTTP_200_OK, response_model=list[ProductResponse])
def get_merchant_products(
        merchant_id: str,
        service: MerchantService = Depends(get_merchant_service)
) -> list[ProductResponse]:
    return service.get_merchant_product(merchant_id)

@router.patch("/{merchant_id}", status_code=status.HTTP_200_OK)
def edit_merchant_account(
    merchant_id: str,
    payload: MerchantUpdate,
    service: MerchantService = Depends(get_merchant_service),
    current_merchant: MerchantResponse = Depends(require_merchant_ownership),
):
    update_data = service.update(str(current_merchant.id), payload)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")
    return update_data