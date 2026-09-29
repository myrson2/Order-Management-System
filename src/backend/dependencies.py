import json
import os
from pathlib import Path

from fastapi import HTTPException, status

from backend.repository.repositories import CustomerRepository, MerchantRepository, ProductRepository, CartRepository, OrderRepository
from backend.schemas.Users.Merchant import MerchantResponse
from backend.service import OrderService
from backend.service.authentication_service import AuthenticationService
from backend.service.customer_service import CustomerService
from backend.service.merchant_services import MerchantService

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001/api/v1")
AUTH_SERVICE_URL = f"/api/v1/auth"
get_base_url = f"/api/v1"

print(API_BASE_URL)

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