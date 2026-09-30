from fastapi import APIRouter, Depends, HTTPException, status
from backend.dependencies import get_base_url, get_order_service, require_customer_ownership
from backend.schemas.Cart import CartCreate, CartResponse, CartUpdate
from backend.schemas.Product import ProductResponse
from backend.schemas.Users import CustomerResponse
from backend.service import OrderService

router = APIRouter(prefix=f"{get_base_url}/cart", tags=["Order"])

@router.post('/customer/{customer_id}/add', status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def add_order(
    customer_id: str,
    cart: CartCreate,
    service: OrderService = Depends(get_order_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP POST endpoint to add a product item to a customer's shopping cart.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        cart (CartCreate): Validated Pydantic CartCreate request body payload.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        CartResponse: Serialized CartResponse schema of the saved cart item.

    Constraints / Notes:
        Returns status 201 Created upon successful persistence into cart.json.
    """
    if str(cart.customer_id) != str(current_customer.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cart customer ID must match the active customer.",
        )
    return service.add_to_cart(cart)

@router.get('/customer/{customer_id}/view', status_code=status.HTTP_200_OK, response_model=list[dict])
def view_cart(
    customer_id: str,
    service: OrderService = Depends(get_order_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP GET endpoint to fetch all active cart items for a specific customer ID.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        list[dict]: List of cart item dictionaries for the specified customer.

    Constraints / Notes:
        Returns empty list [] if no items match the customer ID.
    """
    return service.view_my_cart(str(current_customer.id))

@router.get('/customer/{customer_id}/product/{product_id}/product', status_code=status.HTTP_200_OK, response_model=ProductResponse)
def get_product(
    customer_id: str,
    product_id: str,
    merchant_id: str,
    service: OrderService = Depends(get_order_service),
    _current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP GET endpoint to retrieve product details for a specific product ID and merchant ID.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        product_id (str): Product ID path parameter to look up.
        merchant_id (str): Merchant ID query parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        ProductResponse: Serialized ProductResponse schema if found.

    Constraints / Notes:
        Raises HTTP 404 Exception if the product is not found.
    """
    return service.get_product_by_id(product_id, merchant_id)

@router.get('/customer/{customer_id}/{cart_id}/cart', status_code=status.HTTP_200_OK, response_model=CartResponse)
def get_cart_by_id(
    customer_id: str,
    cart_id: str,
    service: OrderService = Depends(get_order_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP GET endpoint to fetch a single cart item by cart ID and customer ID.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        cart_id (str): Cart item ID path parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        CartResponse: Serialized CartResponse schema of the matching cart item.

    Constraints / Notes:
        Raises HTTP 404 Exception if the cart item is not found.
    """
    return service.get_cart_by_id(cart_id, str(current_customer.id))

@router.patch('/customer/{customer_id}/item/{cart_id}', status_code=status.HTTP_200_OK, response_model=CartResponse)
def edit_cart_item(
    customer_id: str,
    cart_id: str,
    payload: CartUpdate,
    service: OrderService = Depends(get_order_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP PATCH endpoint to partially update fields of an existing cart item.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        cart_id (str): Unique cart item primary key ID string path parameter.
        payload (CartUpdate): Validated Pydantic CartUpdate payload containing optional fields.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        CartResponse: Updated CartResponse schema of the modified cart item.

    Constraints / Notes:
        Raises HTTP 404 Exception if no cart item matches the cart_id and customer_id.
    """
    updated_item = service.update_cart_item(str(current_customer.id), cart_id, payload)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item ID ({cart_id}) not found for customer."
        )
    return updated_item

@router.delete('/customer/{customer_id}/{cart_id}', status_code=status.HTTP_200_OK, response_model=CartResponse)
def delete_cart_item(
    customer_id: str,
    cart_id: str,
    service: OrderService = Depends(get_order_service),
    current_customer: CustomerResponse = Depends(require_customer_ownership),
):
    """
    Description / Purpose:
        HTTP DELETE endpoint to remove a cart item by cart ID and customer ID.

    Args / Parameters:
        customer_id (str): Customer ID path parameter.
        cart_id (str): Cart item primary key ID string path parameter.
        service (OrderService): Injected OrderService dependency instance.

    Returns:
        CartResponse: Deleted CartResponse schema of the removed cart item.

    Constraints / Notes:
        Raises HTTP 404 Exception if the cart item is not found.
    """
    delete_item = service.delete_cart_item(str(current_customer.id), cart_id)
    if not delete_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart item ID ({cart_id}) not found."
        )
    return delete_item

