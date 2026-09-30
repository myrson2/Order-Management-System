import httpx

from backend.schemas.Cart import Cart, CartCreate, CartResponse, CartUpdate
from backend.schemas.Order import OrderResponse
from backend.schemas.Product import ProductResponse
from backend.schemas.Users import CustomerResponse, MerchantResponse
from backend.schemas.Users.Customer import CustomerUpdate
from backend.schemas.Users.Merchant import MerchantUpdate
from backend.service.user_service import UserService
from backend.utilities import API_BASE_URL

class CustomerService(UserService):
    """Business logic and caching service for customer operations."""
    def __init__(self, repositories):
        super().__init__(repositories)
        self.order_items : list[Cart] = []

    @staticmethod
    def _api_request(method: str, path: str, **kwargs) -> httpx.Response:
        """Send a customer-client request and raise on unsuccessful responses.

        Args:
            method: HTTP method to use.
            path: Path relative to the configured API root.
            **kwargs: Additional arguments passed to ``httpx.request``.

        Returns:
            The successful HTTP response.

        Constraints / Notes:
            Uses a five-second timeout and raises HTTPX errors for network or status failures.
        """
        response = httpx.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=5.0,
            **kwargs,
        )
        response.raise_for_status()
        return response

    @staticmethod
    def get_product(customer_id: str, product_id: str, merchant_id: str) -> ProductResponse:
        """Fetch and validate a product for the customer cart flow.

        Args:
            customer_id: Active customer ID.
            product_id: Product ID to retrieve.
            merchant_id: Owner merchant ID for the product.

        Returns:
            The validated product response.

        Constraints / Notes:
            Propagates HTTPX errors when the request fails.
        """
        response = CustomerService._api_request(
            "GET",
            f"/cart/customer/{customer_id}/product/{product_id}/product",
            params={"merchant_id": merchant_id},
        )
        return ProductResponse(**response.json())

    @staticmethod
    def add_cart_item(cart: CartCreate) -> CartResponse:
        """Create a cart item through the API.

        Args:
            cart: Validated cart item request.

        Returns:
            The created cart item response.

        Constraints / Notes:
            The active customer must own the cart customer ID.
        """
        response = CustomerService._api_request(
            "POST",
            f"/cart/customer/{cart.customer_id}/add",
            json=cart.model_dump(mode="json"),
        )
        return CartResponse(**response.json())

    @staticmethod
    def get_cart(customer_id: str) -> list[dict]:
        """Retrieve the active customer's cart contents.

        Args:
            customer_id: Active customer ID.

        Returns:
            Cart item records.

        Constraints / Notes:
            Propagates HTTPX errors when the request fails.
        """
        response = CustomerService._api_request("GET", f"/cart/customer/{customer_id}/view")
        return response.json()

    @staticmethod
    def get_cart_item(customer_id: str, cart_id: str) -> CartResponse:
        """Retrieve one cart item belonging to the active customer.

        Args:
            customer_id: Active customer ID.
            cart_id: Cart item ID to retrieve.

        Returns:
            The validated cart item response.

        Constraints / Notes:
            Propagates HTTPX errors when the request fails.
        """
        response = CustomerService._api_request(
            "GET", f"/cart/customer/{customer_id}/{cart_id}/cart"
        )
        return CartResponse(**response.json())

    @staticmethod
    def update_cart_item(customer_id: str, cart_id: str, update: CartUpdate) -> CartResponse:
        """Update a cart item's editable fields.

        Args:
            customer_id: Active customer ID.
            cart_id: Cart item ID to update.
            update: Validated partial cart update.

        Returns:
            The updated cart item response.

        Constraints / Notes:
            Propagates HTTPX errors when the request fails.
        """
        response = CustomerService._api_request(
            "PATCH",
            f"/cart/customer/{customer_id}/item/{cart_id}",
            json=update.model_dump(exclude_unset=True, mode="json"),
        )
        return CartResponse(**response.json())

    @staticmethod
    def delete_cart_item(customer_id: str, cart_id: str) -> CartResponse:
        """Delete one cart item belonging to the active customer.

        Args:
            customer_id: Active customer ID.
            cart_id: Cart item ID to delete.

        Returns:
            The deleted cart item response.

        Constraints / Notes:
            Propagates HTTPX errors when the request fails.
        """
        response = CustomerService._api_request(
            "DELETE", f"/cart/customer/{customer_id}/{cart_id}"
        )
        return CartResponse(**response.json())

    @staticmethod
    def checkout(customer_id: str) -> OrderResponse:
        """Submit checkout for the active customer's cart.

        Args:
            customer_id: Active customer ID.

        Returns:
            The completed order receipt.

        Constraints / Notes:
            Propagates HTTPX errors when checkout fails.
        """
        response = CustomerService._api_request(
            "POST", f"/order/checkout/{customer_id}"
        )
        return OrderResponse(**response.json())

    @staticmethod
    def get_order_history(customer_id: str) -> list[dict]:
        """Retrieve order history for the active customer.

        Args:
            customer_id: Active customer ID.

        Returns:
            Order receipt records.

        Constraints / Notes:
            Propagates HTTPX errors when the request fails.
        """
        response = CustomerService._api_request(
            "GET", f"/order/customer/{customer_id}"
        )
        return response.json()

    @staticmethod
    def logout_customer(customer: CustomerResponse) -> bool:
        """Request logout for the active customer.

        Args:
            customer: Active customer profile.

        Returns:
            True when the API accepts the logout request.

        Constraints / Notes:
            Propagates HTTPX errors for network failures.
        """
        response = CustomerService._api_request(
            "POST",
            "/auth/logout",
            json=customer.model_dump(mode="json"),
        )
        return response.status_code == 202

    @staticmethod
    def get_stores(base_url: str = API_BASE_URL) -> list[dict]:
        """Fetch store profiles from the merchant API.

        Args:
            base_url: Root API URL.

        Returns:
            Store records returned by the merchant endpoint.

        Constraints / Notes:
            Raises HTTPX request or status exceptions when the API is unavailable.
        """
        response = httpx.get(f"{base_url}/merchant/", timeout=5.0)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_store_products(store_name: str) -> list[dict]:
        """Return products belonging to the named store.

        Args:
            store_name: Store name to look up.

        Returns:
            Products belonging to the store, or an empty list if it has none or is unknown.

        Constraints / Notes:
            Raises HTTPX request or status exceptions when the API is unavailable.
        """
        stores_response = httpx.get(f"{API_BASE_URL}/merchant/", timeout=5.0)
        stores_response.raise_for_status()
        merchant = next(
            (store for store in stores_response.json() if store.get("store_name") == store_name),
            None,
        )
        if merchant is None:
            return []

        products_response = httpx.get(f"{API_BASE_URL}/merchant/products", timeout=5.0)
        products_response.raise_for_status()
        merchant_id = str(merchant.get("id"))
        return [
            product
            for product in products_response.json()
            if str(product.get("merchant_id")) == merchant_id
        ]

    @staticmethod
    def get_merchant(store_name: str) -> MerchantResponse | None:
        """Find a merchant profile by store name.

        Args:
            store_name: Store name to search for.

        Returns:
            A validated merchant profile, or None when no store matches.

        Constraints / Notes:
            Raises HTTPX request or status exceptions when the API is unavailable.
        """
        response = httpx.get(f"{API_BASE_URL}/merchant/", timeout=5.0)
        response.raise_for_status()
        for merchant in response.json():
            if merchant.get("store_name") == store_name:
                return MerchantResponse(**merchant)
        return None

    def update(self, user_id: str, user_data: MerchantUpdate | CustomerUpdate) -> dict | None:
        """Apply and persist allowed profile changes for an existing customer.

        Args:
            customer_id: ID of the customer to update.
            user_data: Validated partial profile update.

        Returns:
            Updated JSON-ready customer data, or None if no customer exists.

        Constraints / Notes:
            Immutable identity fields are not accepted; empty updates leave storage unchanged.
        """
        customer = self.get_user_by_id(user_id)
        if customer is None:
            return None

        CustomerResponse(**customer)
        changes = user_data.model_dump(exclude_unset=True, exclude_none=True, mode="json")
        if changes:
            updated_customer = {**customer, **changes}
            validated_customer = CustomerResponse(**updated_customer)
            customer.update(validated_customer.model_dump(mode="json"))
            self.save_cache()
        return CustomerResponse(**customer).model_dump(mode="json")
