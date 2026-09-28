from typing import Any

import httpx

from backend.schemas.Cart import Cart
from backend.schemas.Users import Customer, MerchantResponse
from backend.service.user_service import UserService

class CustomerService(UserService):
    """Business logic and caching service for customer operations."""
    def __init__(self, repositories):
        super().__init__(repositories)
        self.order_items : list[Cart] = []

    @staticmethod
    def get_stores(base_url: str) -> list[dict]:
        try:
            # Merchants (stores) are located at the /merchant/ endpoint
            response = httpx.get(f'{base_url}/merchant/', timeout=5.0)

            if response.status_code == 200:
                stores = response.json()
                return stores
            else:
                print(f"\n[API ERROR {response.status_code}]: {response.text}")
                return []
        except httpx.RequestError as e:
            print(f"\n[API ERROR] Network error: {e}")
            return []

    @staticmethod
    def get_store_products(store_name: str) -> list[Any] | None:
        try:
            response = httpx.get('http://127.0.0.1:8001/api/v1/merchant/', timeout=5.0)
            if response.status_code == 200:
                response_json = response.json()

                get_merchant_id = None
                for response in response_json:
                    if response.get("store_name") == store_name:
                        get_merchant_id = response.get("id")

                if not get_merchant_id:
                    print(f"Store name, {store_name} not found")
                    return None

                get_products = httpx.get('http://127.0.0.1:8001/api/v1/merchant/products')

                if get_products.status_code == 200:
                    products_json = get_products.json()

                    products = [product for product in products_json if product.get('merchant_id') == get_merchant_id]
                    if not products:
                        print("\n[INFO] This store currently has no products.")
                    else:
                       return products
            else:
                print(f"\n[API ERROR {response.status_code}]: {response.text}")
        except httpx.RequestError as e:
            print(f"\n[API ERROR] Network failed: {e}")

    @staticmethod
    def get_merchant(store_name) -> MerchantResponse | None:
        try:
            response = httpx.get('http://127.0.0.1:8001/api/v1/merchant/', timeout=5.0)
            if response.status_code == 200:
                for response in response.json():
                    if response.get("store_name") == store_name:
                        return MerchantResponse(**response)
                return None
            else:
                return None
        except httpx.RequestError as e:
            print(e)

    def update(self, user_data):
        pass
