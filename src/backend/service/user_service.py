from abc import abstractmethod, ABC
from src.backend.schemas.Users.Merchant import MerchantUpdate
from src.backend.schemas.Users.Customer import CustomerUpdate

class UserService(ABC):
    """Base business logic and caching service for user entities."""

    def __init__(self, repositories) -> None:
        """
        Description / Purpose:
            Initializes UserService with a repository dependency, initializes the
            in-memory cache list, and loads initial records from storage.

        Args / Parameters:
            repositories: Repository instance adhering to Repository abstract base class.

        Returns:
            None.

        Constraints / Notes:
            Automatically triggers _load_cache() during object initialization.
        """
        self.repositories = repositories
        self.cache: list[dict] = []
        self._load_cache()

    def _load_cache(self) -> None:
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
        for data in self.repositories.load_repo():
            self.cache.append(data)

    def save_cache(self) -> None:
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
        json_data = [data for data in self.cache]
        self.repositories.save_repo(json_data)

    def get_all(self) -> list[dict]:
        """
        Description / Purpose:
            Retrieves the full list of cached entity dictionaries currently held in memory.

        Args / Parameters:
            None.

        Returns:
            list[dict]: List of serialized entity dictionaries from the cache.

        Constraints / Notes:
            Returns direct reference to the in-memory cache list.
        """
        return self.cache

    def get_user_by_id(self, customer_id: str) -> dict | None:
        """
        Description / Purpose:
            Searches the in-memory cache for an entity matching the given unique ID string.

        Args / Parameters:
            customer_id (str): Unique entity UUID or ID string to locate.

        Returns:
            dict | None: The matching entity dictionary if found, or None.

        Constraints / Notes:
            Compares string representations of IDs to prevent UUID/string mismatch errors.
        """
        customers = self.get_all()
        for c in customers:
            if str(c.get("id")) == str(customer_id):
                return c
        return None

    def add(self, user_data: dict) -> None:
        """
        Description / Purpose:
            Appends a new entity record to the in-memory cache and persists changes to storage.

        Args / Parameters:
            user_data (dict): Serialized entity dictionary payload.

        Returns:
            None.

        Constraints / Notes:
            Immediately calls save_cache() to maintain cache-to-disk consistency.
        """
        self.cache.append(user_data)
        self.save_cache()

    @abstractmethod
    def update(self, user_id: str, user_data: MerchantUpdate | CustomerUpdate) -> dict | None:
        pass









