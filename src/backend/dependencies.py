import json
from pathlib import Path

from fastapi import Depends, HTTPException, status

from backend.repository.repositories import CustomerRepository, MerchantRepository, ProductRepository, CartRepository, OrderRepository
from backend.schemas.Users import CustomerResponse
from backend.schemas.Users.Merchant import MerchantResponse
from backend.service import OrderService
from backend.service.authentication_service import AuthenticationService
from backend.service.customer_service import CustomerService
from backend.service.merchant_services import MerchantService
from backend.utilities import API_BASE_URL

AUTH_SERVICE_URL = f"/api/v1/auth"
get_base_url = f"/api/v1"

target_path = Path(__file__).resolve().parent / "database"
customer_path = target_path / "customer.json"
merchant_path = target_path / "merchant.json"
product_path = target_path / "product.json"
cart_path = target_path / "cart.json"
order_path = target_path / "order.json"

if not customer_path.exists():
    with open(customer_path, "w", encoding="utf-8") as file:
        json.dump([], file)

if not merchant_path.exists():
    with open(merchant_path, "w", encoding="utf-8") as file:
        json.dump([], file)

if not product_path.exists():
    with open(product_path, "w", encoding="utf-8") as file:
        json.dump([], file)

if not cart_path.exists():
    with open(cart_path, "w", encoding="utf-8") as file:
        json.dump([], file)

if not order_path.exists():
    with open(order_path, "w", encoding="utf-8") as file:
        json.dump([], file)

customer_repo = CustomerRepository(customer_path)
merchant_repo = MerchantRepository(merchant_path)
product_repo = ProductRepository(product_path)
cart_repo = CartRepository(cart_path)
order_repo = OrderRepository(order_path)

order_service = OrderService(cart_repo, product_repo, order_repo)
customer_service = CustomerService(customer_repo)
merchant_service = MerchantService(merchant_repo, product_repo)

authentication_service = AuthenticationService(customer_service, merchant_service)

_active_merchant_id: str | None = None
_active_customer_id: str | None = None

def set_current_customer_id(customer_id: str | None) -> None:
    """Set the active customer identity used by customer-owned routes.

    Args:
        customer_id: Customer ID to activate, or None to clear the session.

    Returns:
        None.

    Constraints / Notes:
        Stores one process-local active customer ID.
    """
    global _active_customer_id
    _active_customer_id = str(customer_id) if customer_id is not None else None

def clear_current_customer_id() -> None:
    """Clear the process-local active customer identity.

    Args:
        None.

    Returns:
        None.

    Constraints / Notes:
        Customer-owned routes return 401 until another customer logs in.
    """
    global _active_customer_id
    _active_customer_id = None

def get_current_customer() -> CustomerResponse:
    """Resolve the active customer profile for FastAPI dependencies.

    Args:
        None.

    Returns:
        The validated active customer profile.

    Constraints / Notes:
        Raises HTTP 401 when no customer is active and 404 if its record is missing.
    """
    global _active_customer_id

    if _active_customer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active customer session."
        )

    customer_data = customer_service.get_user_by_id(_active_customer_id)
    if customer_data is None:
        clear_current_customer_id()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active customer session not found."
        )

    return CustomerResponse(**customer_data)

def require_customer_ownership(
    customer_id: str,
    current_customer: CustomerResponse = Depends(get_current_customer),
) -> CustomerResponse:
    """Require a route's customer ID to match the active customer session.

    Args:
        customer_id: Customer ID supplied in the route path.
        current_customer: Customer resolved from the active session.

    Returns:
        The active customer when the IDs match.

    Constraints / Notes:
        Raises HTTP 403 when the requested customer is not the active customer.
    """
    if str(current_customer.id) != str(customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this customer account.",
        )
    return current_customer

def set_current_merchant_id(merchant_id: str | None) -> None:
    global _active_merchant_id
    _active_merchant_id = str(merchant_id) if merchant_id is not None else None

def clear_current_merchant_id() -> None:
    global _active_merchant_id
    _active_merchant_id = None

def get_current_merchant() -> MerchantResponse:
    global _active_merchant_id

    if _active_merchant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active merchant session."
        )

    merchant_data = merchant_service.get_user_by_id(_active_merchant_id)
    if merchant_data is None:
        clear_current_merchant_id()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active merchant session not found."
        )

    return MerchantResponse(**merchant_data)

def require_merchant_ownership(
    merchant_id: str,
    current_merchant: MerchantResponse = Depends(get_current_merchant),
) -> MerchantResponse:
    """Require a route's merchant ID to match the active merchant session.

    Args:
        merchant_id: Merchant ID supplied in the route path.
        current_merchant: Merchant resolved from the active session.

    Returns:
        The active merchant when the IDs match.

    Constraints / Notes:
        Raises HTTP 403 when the requested merchant is not the active merchant.
    """
    if str(current_merchant.id) != str(merchant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to manage this merchant account.",
        )
    return current_merchant


def get_auth_service() -> AuthenticationService:
    """
    Description / Purpose:
        FastAPI dependency provider returning the singleton instance of AuthenticationService.

    Args / Parameters:
        None.

    Returns:
        AuthenticationService: Shared authentication service instance.

    Constraints / Notes:
        Used with FastAPI Depends() dependency injection in authentication controller routes.
    """
    return authentication_service

def get_customer_service() -> CustomerService:
    """
    Description / Purpose:
        FastAPI dependency provider returning the singleton instance of CustomerService.

    Args / Parameters:
        None.

    Returns:
        CustomerService: Shared customer service instance.

    Constraints / Notes:
        Used with FastAPI Depends() dependency injection in controller routes.
    """
    return customer_service

def get_merchant_service() -> MerchantService:
    """
    Description / Purpose:
        FastAPI dependency provider returning the singleton instance of MerchantService.

    Args / Parameters:
        None.

    Returns:
        MerchantService: Shared merchant service instance.

    Constraints / Notes:
        Used with FastAPI Depends() dependency injection in controller routes.
    """
    return merchant_service

def get_order_service() -> OrderService:
    return order_service