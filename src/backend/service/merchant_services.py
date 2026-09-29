import httpx

from backend.repository.repositories import ProductRepository
from backend.schemas.Product import ProductCreate, ProductResponse, ProductUpdate
from backend.schemas.Users import MerchantResponse, Customer
from backend.schemas.Users.Customer import CustomerUpdate
from backend.schemas.Users.Merchant import MerchantUpdate
from backend.service.user_service import UserService

class MerchantService(UserService):
    """Business logic and caching service for merchant operations."""
    def __init__(self,
                 repositories,
                 product_repository:
                 ProductRepository) -> None:
        """
        Description / Purpose:
            Initializes the MerchantService with user and product repositories,
            and preloads the in-memory product cache.

        Args / Parameters:
            repositories: Repository instance for merchant user data.
            product_repository (ProductRepository): Repository instance for product persistence.

        Returns:
            None.

        Constraints / Notes:
            Calls super().__init__ to set up base user caching, then populates product_cache.
        """
        super().__init__(repositories)
        self.product_repository = product_repository
        self.product_cache: list[dict] = []
        self._load_product_cache()

    def _load_product_cache(self) -> None:
        """
        Description / Purpose:
            Loads entity records from the repository into the in-memory cache list.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Private helper method called during initialization to populate cache.
        """
        for data in self.product_repository.load_repo():
            self.product_cache.append(data)

    def save_product_cache(self) -> None:
        """
        Description / Purpose:
            Persists the in-memory cache list to storage via the underlying repository.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Calls repositories.save_repo() with a snapshot of the current cache contents.
        """
        json_data_products = [products for products in self.product_cache]
        self.product_repository.save_repo(json_data_products)

    def get_all_products(self) -> list[dict]:
        """
        Description / Purpose:
            Retrieves the full list of products currently cached in memory.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of product dictionary records from the in-memory cache.

        Constraints / Notes:
            Returns a direct reference to product_cache without database reads.
        """
        return self.product_cache

    def get_merchant_product(self,
                             merchant_id: str
                        ) -> list[ProductResponse]:
        merchant_products = [ProductResponse(**merchant) for merchant in self.product_cache if merchant_id == merchant['merchant_id']]
        return merchant_products

    def add_product(self,
                    product: ProductCreate
                ) -> ProductResponse:
        """
        Description / Purpose:
            Appends a newly created product to the catalog, persists changes to storage,
            and returns the validated ProductResponse model.

        Args / Parameters:
            product (ProductCreate): Validated schema containing product attributes and generated ID.

        Returns:
            ProductResponse: Strongly-typed schema representing the persisted product.

        Constraints / Notes:
            Persists synchronously to storage via self.save_product_cache().
        """
        product_dict = product.to_dict()
        self.product_cache.append(product_dict)
        self.save_product_cache()
        return ProductResponse(**product_dict)

    def delete_product(self,
                       product_id: str,
                       merchant_id: str
                    ) -> dict[str, str] | ProductResponse | None:
        """
        Description / Purpose:
            Removes a product from the in-memory cache and persists the change to storage,
            ensuring the product belongs to the requesting merchant.

        Args / Parameters:
            product_id (str): Unique identifier of the product to delete.
            merchant_id (str): UUID string of the merchant requesting deletion.

        Returns:
            ProductResponse | None: ProductResponse instance of the deleted product, or None if not found/unauthorized.

        Constraints / Notes:
            Verifies both product ID and merchant ownership before mutating product_cache.
        """

        response = httpx.get(f"http://127.0.0.1:8001/api/v1/merchant/{merchant_id}/products/{product_id}")

        if response.status_code == 404:
            return {
                'description': f'{response.text}',
                'status': f'{response.status_code}',
            }
        else:
            for index, products in enumerate(self.product_cache):
                if products.get('merchant_id') == str(merchant_id):
                    products = self.product_cache.pop(index)
                    self.save_product_cache()
                    return ProductResponse(**products)
        return None

    def get_product_by_id(self,
                          product_id: str,
                          merchant_id: str
                        ) -> ProductResponse | None:
        """
        Description / Purpose:
            Searches the in-memory product cache for a product matching the given ID.

        Args / Parameters:
            product_id (str): Unique product identifier string to look up.

        Returns:
            dict | None: The matching product dictionary if found, or None.

        Constraints / Notes:
            Scans product_cache linearly by key 'id'.
        """
        for index, products in enumerate(self.product_cache):
            if products.get('id') == product_id and str(products.get('merchant_id')) == str(merchant_id):
                return ProductResponse(**products)
        return None

    def update_product(
        self,
        merchant_id: str,
        product_id: str,
        product_update: ProductUpdate
    ) -> ProductResponse | None:
        """
        Description / Purpose:
            Updates product fields (such as stock level, price, or name) in the in-memory cache
            and persists changes to storage, ensuring merchant ownership verification.

        Args / Parameters:
            merchant_id (str): UUID string of the merchant requesting the update.
            product_id (str): Unique product identifier string to update.
            product_update (ProductUpdate): Validated partial product update schema.

        Returns:
            ProductResponse | None: The updated ProductResponse model if found and modified, or None.

        Constraints / Notes:
            Uses exclude_unset=True to only update attributes that were explicitly provided.
        """
        for product in self.product_cache:
            if product.get('id') == product_id and str(product.get('merchant_id')) == str(merchant_id):
                update_fields = product_update.model_dump(exclude_unset=True)
                if not update_fields:
                    return ProductResponse(**product)

                product.update(update_fields)
                self.save_product_cache()
                return ProductResponse(**product)
        return None

    def update(
        self,
        merchant_id: str,
        user_data: MerchantUpdate | CustomerUpdate,
    ) -> dict | None:
        """Update a merchant profile and persist the changed cache record.

        Args:
            merchant_id: ID of the merchant to update.
            user_data: Profile update payload; customer payloads are not accepted.

        Returns:
            Public merchant data as a JSON-ready dictionary, or None if not found
            or the payload is for a customer.
        """
        if not isinstance(user_data, MerchantUpdate):
            return None

        merchant = self.get_user_by_id(str(merchant_id))
        if merchant is None:
            return None

        data = user_data.model_dump(exclude_none=True, mode="json")
        if data:
            merchant.update(data)
            self.save_cache()

        return MerchantResponse(**merchant).model_dump(mode="json")
