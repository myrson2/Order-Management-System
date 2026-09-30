from typing import TypeVar
from backend.schemas.Users import Customer, Merchant
from backend.schemas.Users.Customer import CustomerResponse
from backend.schemas.Users.Merchant import MerchantResponse
from backend.schemas.Users.User import UserLogin, UserResponse, EnumType, ActiveStatus
from backend.service.customer_service import CustomerService
from backend.service.merchant_services import MerchantService

UserT = TypeVar("UserT", Customer, Merchant)

def _find_user_in_repo(repo: list[dict], email: str, password: str, model_class: type[UserT]) -> UserT | None:
    """
    Description / Purpose:
        Searches an in-memory repository cache list for matching email and password,
        and returns an instantiated model instance if found.

    Args / Parameters:
        repo (list[dict]): The in-memory cache list of user dictionaries.
        email (str): The email address to look for.
        password (str): The plain-text password to compare against.
        model_class (type[T]): The target Pydantic class to instantiate (Customer or Merchant).

    Returns:
        T | None: Instantiated model instance if match is found, or None.

    Constraints / Notes:
        Compares plain text credentials; relies on model_class.from_dict for instantiation.
    """
    if not repo:
        return None

    match = next(
        (item for item in repo if item.get("email") == email and item.get("password") == password),
        None
    )
    return model_class.from_dict(match) if match else None

class AuthenticationService:
    """Handles authentication lifecycle, status toggling, and user session validation."""

    def __init__(self, customer_service: CustomerService, merchant_service: MerchantService) -> None:
        """
        Description / Purpose:
            Initializes AuthenticationService with customer and merchant domain service dependencies.

        Args / Parameters:
            customer_service (CustomerService): Customer service managing customer records and cache.
            merchant_service (MerchantService): Merchant service managing merchant records and cache.

        Returns:
            None.

        Constraints / Notes:
            Stores references for user lookups and active status updates across domains.
        """
        self.customer_service = customer_service
        self.merchant_service = merchant_service

    @staticmethod
    def _set_active_status(
        service: CustomerService | MerchantService,
        user_id: str,
        active_status: ActiveStatus,
    ) -> bool:
        """Update a cached user record's status and persist the cache.

        Args:
            service: User service that owns the record.
            user_id: ID of the user whose status should change.
            active_status: Status value to persist.

        Returns:
            True if the user record was found and saved, otherwise False.

        Constraints / Notes:
            Mutates the cached record and immediately writes the full cache through its repository.
        """
        user_data = service.get_user_by_id(user_id)
        if user_data is None:
            return False

        user_data["active_status"] = active_status.value
        service.save_cache()
        return True

    def login(self, user: UserLogin) -> UserResponse | None:
        """
        Description / Purpose:
            Authenticates user credentials against customer and merchant caches, sets
            the matched user's active status to online, and returns safe UserResponse DTO.

        Args / Parameters:
            user (UserLogin): Validated login payload containing email and password.

        Returns:
            UserResponse | None: Safe response model (CustomerResponse or MerchantResponse) or None if invalid.

        Constraints / Notes:
            Searches customer cache first, then merchant cache. Persists updated online status.
        """
        email = user.email
        password = user.password

        # Check customer
        customer = _find_user_in_repo(self.customer_service.cache, email, password, Customer)
        if customer is not None:
            if not self._set_active_status(
                self.customer_service,
                str(customer.id),
                ActiveStatus.ONLINE,
            ):
                return None
            customer.online()
            return CustomerResponse(**customer.model_dump())

        # Check merchant
        merchant = _find_user_in_repo(self.merchant_service.cache, email, password, Merchant)
        if merchant is not None:
            if not self._set_active_status(
                self.merchant_service,
                str(merchant.id),
                ActiveStatus.ONLINE,
            ):
                return None
            merchant.online()
            return MerchantResponse(**merchant.model_dump())

        return None

    def logout(self, user_res: UserResponse) -> bool:
        """
        Description / Purpose:
            Logs out an authenticated user by locating their record, setting active_status
            to OFFLINE, and persisting the updated state.

        Args / Parameters:
            user_res (UserResponse): DTO representing the currently logged-in user.

        Returns:
            bool: True if user was found and updated to offline, False otherwise.

        Constraints / Notes:
            Validates user_type against EnumType explicitly. Returns False if user ID is missing.
        """
        # 1. Map each user_type to the responsible service
        service_map = {
            EnumType.MERCHANT: self.merchant_service,
            EnumType.CUSTOMER: self.customer_service,
        }

        # 2. Pick the target service in one clean line
        service = service_map.get(user_res.user_type)
        if not service:
            return False

        # 3. Perform the logout logic ONCE for ANY user type!
        raw_data = service.get_user_by_id(str(user_res.id))
        if not raw_data:
            return False

        # 4. Update status and persist cache
        raw_data["active_status"] = ActiveStatus.OFFLINE.value
        service.save_cache()
        return True

