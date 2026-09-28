import httpx
from backend.schemas.Users import MerchantResponse
from backend.schemas.Product import ProductCreate, ProductResponse, ProductUpdate
from pydantic import ValidationError
from typing import Literal

from backend.schemas.Users.Merchant import MerchantUpdate


class MerchantInterface:
    """Business logic for managing merchant transactions."""
    def __init__(self, current_merchant: MerchantResponse) -> None:
        """
        Description / Purpose:
            Initializes MerchantInterface with the active merchant's session data
            and constructs the scoped API URL for merchant routes.

        Args / Parameters:
            current_merchant (MerchantResponse): Currently authenticated merchant session object.

        Returns:
            None.

        Constraints / Notes:
            Scopes self.url to http://127.0.0.1:8000/api/v1/merchant/{merchant_id}.
        """
        self.current_merchant = current_merchant
        self.base_url = "http://127.0.0.1:8001/api/v1/merchant"
        self.url = f"http://127.0.0.1:8001/api/v1/merchant/{current_merchant.id}"

    def __str__(self) -> str:
        """
        Description / Purpose:
            Returns a friendly informal greeting string identifying the merchant by full name.

        Args / Parameters:
            None.

        Returns:
            str: Greeting string including merchant's first and last name.

        Constraints / Notes:
            Reads attributes directly from self.current_merchant.
        """
        return f"Hello {self.current_merchant.first_name} {self.current_merchant.last_name}"

    def welcome_message(self) -> str:
        """
        Description / Purpose:
            Formats and returns a welcome banner string with merchant name and email.

        Args / Parameters:
            None.

        Returns:
            str: Formatted welcome message string.

        Constraints / Notes:
            Reads directly from self.current_merchant attributes.
        """
        return f"\nLogged in as: {self.current_merchant.first_name} {self.current_merchant.last_name} ({self.current_merchant.email})"

def merchant_menu() -> None:
    """
    Description / Purpose:
        Displays the Merchant Management menu options for product inventory and account settings.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII options to the terminal console.
    """
    print("\n" + "=" * 40)
    print("        MERCHANT MANAGEMENT MENU        ")
    print("=" * 40)
    print("1. Add Product")
    print("2. Update Stock")
    print("3. Edit Stock")
    print("4. Delete Stock")
    print("5. Settings")
    print("=" * 40)

def settings_menu() -> None:
    """
    Description / Purpose:
        Displays the merchant account settings and session options.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII menu options to the terminal console.
    """
    print("\n" + "=" * 40)
    print("            SETTINGS MENU               ")
    print("=" * 40)
    print("1. Edit User Profile")
    print("2. Logout")
    print("3. Back to Merchant Menu")
    print("=" * 40)

def update_stock_menu() -> None:
    """
    Description / Purpose:
        Displays the stock management submenu options (Deduct Stock, Restock).

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII menu options to the terminal console.
    """
    print("\n" + "=" * 40)
    print("          UPDATE STOCK MENU             ")
    print("=" * 40)
    print("1. Deduct Stock")
    print("2. Restock")
    print("3. Back to Merchant Menu")
    print("=" * 40)

def edit_profile_flow(merchant: MerchantInterface) -> None:
    """
    Description / Purpose:
        Interactive CLI flow allowing a merchant to update their profile details.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Feature stub awaiting profile update endpoint wiring.
    """

    print("Space if u dont want to edit.")
    f_name = input("Edit First Name: ").strip()
    l_name = input("Edit Last Name: ").strip()
    change_store_name = input("Edit Store Name: ").strip()

    patch_data = MerchantUpdate(
        id=merchant.current_merchant.id,
        first_name=f_name,
        last_name=l_name,
        store_name=change_store_name,
    )

    response = httpx.patch(f'{merchant.url}', json=patch_data.model_dump(exclude_none=True, mode='json'))

    if response.status_code == 404:
        print(f"\n[LOG] {response.text}")

    if response.status_code == 200:
        print(response.json())

def handle_settings(merchant: MerchantInterface) -> bool:
    """
    Description / Purpose:
        Controls the interactive settings loop for the merchant, handling profile edits and logout.

    Args / Parameters:
        current_merchant (MerchantResponse): Currently authenticated merchant session.

    Returns:
        bool: True if the merchant logged out successfully, False to return to merchant menu.

    Constraints / Notes:
        Sends HTTP POST to /api/v1/auth/logout via httpx and handles network exceptions.
    """
    while True:
        settings_menu()
        choice = input("Select an option (1-3): ").strip()

        match choice:
            case "1":
                print("\n[Action] Edit User Profile selected.")
                edit_profile_flow(merchant)
            case "2":
                try:
                    response = httpx.post("http://127.0.0.1:8001/api/v1/auth/logout",
                                          json=merchant.current_merchant.model_dump(mode='json'))
                    print(f"\n[LOGOUT] Logging out {merchant.current_merchant.first_name} {merchant.current_merchant.last_name}...")

                    if response.status_code == 200:
                        print(f"\n[LOGOUT] Successfully logged out {merchant.current_merchant.first_name} {merchant.current_merchant.last_name}.")
                        return True
                    else:
                        print(f"\n[ERROR] Logout failed with status code {response.status_code}: {response.text}")

                except httpx.RequestError as e:
                    print(f"\n[API ERROR] Could not connect to server for logout: {e}")
            case "3":
                print("\nReturning to Merchant Menu...")
                return False
            case _:
                print("\n[ERROR] Invalid option. Please enter 1-3.")

def add_product_flow(merchant: MerchantInterface) -> None:
    """
    Description / Purpose:
        Interactive user input flow to collect product details, validate them
        via the Product schema, and submit to the backend API.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant interface instance containing session and URL.

    Returns:
        None.

    Constraints / Notes:
        Catches ValidationError from Pydantic and RequestError from httpx to prevent CLI crashes.
    """
    print("\n" + "=" * 40)
    print("           ADD NEW PRODUCT              ")
    print("=" * 40)

    try:
        product_name = input("Enter Product Name: ").strip()

        unit_price_raw = input("Enter Unit Price (e.g., 29.99): ").strip()
        try:
            unit_price = float(unit_price_raw)
        except ValueError:
            print("\n[INPUT ERROR] Unit price must be a valid numeric value.")
            return

        stock_quantity_raw = input("Enter Stock Quantity (e.g., 100): ").strip()
        try:
            stock_quantity = int(stock_quantity_raw)
        except ValueError:
            print("\n[INPUT ERROR] Stock quantity must be a valid integer.")
            return

        # Instantiate Product schema to trigger field validators
        product = ProductCreate(
            merchant_id=merchant.current_merchant.id,
            product_name=product_name,
            unit_price=unit_price,
            stock_quantity=stock_quantity
        )

        # Submit to merchant's scoped endpoint: POST /api/v1/merchant/{merchant_id}/products
        url = f"{merchant.url}/products"
        response = httpx.post(url, json=product.to_dict(), timeout=5.0)

        if response.status_code in (200, 201):
            created_data = ProductResponse(**response.json())
            print(f"\n[SUCCESS] Product '{created_data.product_name}' (ID: {created_data.id}) successfully added!")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except ValidationError as e:
        for err in e.errors():
            field = " -> ".join(str(loc) for loc in err.get("loc", []))
            print(f"\n[VALIDATION ERROR] {field}: {err.get('msg')}")
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")

def print_product_table(products: list[dict]) -> None:
    """
    Description / Purpose:
        Renders a list of product records in a formatted ASCII table with '|' column borders.

    Args / Parameters:
        products (list[dict]): Collection of product dictionaries to format and display.

    Returns:
        None.

    Constraints / Notes:
        Handles empty collections gracefully and truncates product names longer than 25 characters.
    """
    if not products:
        print("\n[INFO] No products found in the catalog.")
        return

    separator = "-" * 75
    print("\n" + separator)
    print(f"| {'ID':<12} | {'Product Name':<25} | {'Unit Price':<12} | {'Stock':<10} |")
    print(separator)
    for p in products:
        p_id = str(p.get("id", "N/A"))
        name = str(p.get("product_name", "N/A"))[:25]
        price = f"${float(p.get('unit_price', 0.0)):.2f}"
        stock = str(p.get("stock_quantity", 0))
        print(f"| {p_id:<12} | {name:<25} | {price:<12} | {stock:<10} |")
    print(separator + "\n")

def display_all_products(merchant: MerchantInterface) -> list[dict]:
    """
    Description / Purpose:
        Fetches the complete catalog of products from the backend API
        and renders them in a formatted table with '|' column separators.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant interface instance containing base URL info.

    Returns:
        list[dict]: List of product dictionaries retrieved from the API, or empty list on network error.

    Constraints / Notes:
        Handles httpx.RequestError gracefully if backend connection fails.
    """
    try:
        response = httpx.get(f"{merchant.url}/products", timeout=5.0)
        if response.status_code == 200:
            products = response.json()
            print_product_table(products)
            return products
        print(f"\n[API ERROR {response.status_code}]: {response.text}")
        return []
    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")
        return []

def delete_stock_flow(product_id: str, merchant: MerchantInterface) -> ProductResponse | None:
    """
    Description / Purpose:
        Sends an HTTP DELETE request to remove a specific product from the merchant's catalog.

    Args / Parameters:
        product_id (str): The unique identifier of the product to delete.
        merchant (MerchantInterface): The active merchant interface containing session and URL configurations.
        all_products (list | None): Optional cached list of current products.

    Returns:
        None.

    Constraints / Notes:
        Handles httpx.RequestError for network failures and checks HTTP status codes
        (200/204 for success, 404 for missing items, and other unexpected status codes).
    """
    try:
        response = httpx.delete(f"{merchant.url}/products/{product_id}", timeout=5.0)

        if response.status_code == 200:
            # 1. Parse the JSON body from the HTTP response
            payload = response.json()

            # 2. Feed it into your Pydantic schema!
            deleted_product = ProductResponse(**payload)

            # 3. Now you have full access to typed attributes!
            print(f"\n[SUCCESS] Product '{deleted_product.product_name}' (ID: {product_id}) was successfully deleted.")

        elif response.status_code == 404:
            print(f"\n[NOT FOUND] No product matches ID '{product_id}'. Please verify the ID and try again.")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")

def adjust_stock_flow(
    merchant: MerchantInterface,
    quantity: int,
    product_data: ProductResponse,
    action: Literal["restock", "deduct"]
) -> None:
    """
    Description / Purpose:
        Calculates updated stock level based on action type, validates inputs,
        and transmits a PATCH request to update the product stock on the backend.

    Args / Parameters:
        merchant (MerchantInterface): The active merchant session containing URL configurations.
        quantity (int): Number of units to add or subtract.
        product_data (ProductResponse): The current product schema model instance.
        action (Literal["restock", "deduct"]): Direction of inventory adjustment.

    Returns:
        None.
    """
    # 1. Validate numeric input
    try:
        amount = int(quantity)
        if amount <= 0:
            print(f"\n[INPUT ERROR] {action.capitalize()} quantity must be greater than zero.")
            return
    except ValueError:
        print("\n[INPUT ERROR] Please enter a valid whole number.")
        return

    # 2. Compute new stock level and target endpoint
    if action == "restock":
        new_stock = product_data.stock_quantity + amount
    elif action == "deduct":
        if amount > product_data.stock_quantity:
            print(f"\n[INPUT ERROR] Cannot deduct {amount}. Available stock is only {product_data.stock_quantity}.")
            return
        new_stock = product_data.stock_quantity - amount
    else:
        print(f"\n[ERROR] Unsupported action '{action}'. Must be 'restock' or 'deduct'.")
        return

    # 3. Serialize update payload
    payload = ProductUpdate(stock_quantity=new_stock).model_dump(exclude_unset=True)

    # 4. Transmit request
    try:
        url = f"{merchant.url}/products/{product_data.id}/edit"
        response = httpx.patch(url, json=payload, timeout=5.0)

        if response.status_code == 200:
            product_data.stock_quantity = new_stock
            print(f"\n[SUCCESS] Successfully completed {action} for '{product_data.product_name}'!")
            print(f"New Stock Level: {product_data.stock_quantity}")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")


def update_stock_flow(merchant: MerchantInterface, product_data: ProductResponse) -> None:
    """
    Description / Purpose:
        Interactive user input flow displaying the stock adjustment submenu (Deduct / Restock),
        prompting for adjustment quantity, and executing adjust_stock_flow.

    Args / Parameters:
        merchant (MerchantInterface): Active merchant session with API routing configurations.
        product_data (ProductResponse): The target product schema instance to be adjusted.

    Returns:
        None.

    Constraints / Notes:
        Loops until merchant selects option 3 to exit back to the Merchant Management menu.
        Validates integer input for quantity before invoking adjust_stock_flow.
    """
    while True:
        print(f"\nProduct: {product_data.product_name} | Current Stock: {product_data.stock_quantity}")
        update_stock_menu()
        choice = input("Select an option (1-3): ").strip()

        match choice:
            case "1":
                print("\n[Action] Deduct Stock selected.")
                raw_qty = input("Enter quantity to deduct: ").strip()
                try:
                    qty = int(raw_qty)
                    adjust_stock_flow(merchant, qty, product_data, "deduct")
                except ValueError:
                    print("\n[INPUT ERROR] Please enter a valid whole number.")
            case "2":
                print("\n[Action] Restock selected.")
                raw_qty = input("Enter quantity to add: ").strip()
                try:
                    qty = int(raw_qty)
                    adjust_stock_flow(merchant, qty, product_data, "restock")
                except ValueError:
                    print("\n[INPUT ERROR] Please enter a valid whole number.")
            case "3":
                print("\nReturning to Merchant Menu...")
                break
            case _:
                print("\n[ERROR] Invalid option. Please select 1-3.")


def edit_stock_flow(my_merchant: MerchantInterface, product_data: ProductResponse) -> None:
    """
    Description / Purpose:
        Prompts merchant to edit the product name and unit price (excluding stock quantity),
        validates the inputs via ProductUpdate schema, and sends a PATCH request to the backend.

    Args / Parameters:
        my_merchant (MerchantInterface): Active merchant session with scoped URL configurations.
        product_data (ProductResponse): The target product schema instance to be edited.

    Returns:
        None.

    Constraints / Notes:
        Validates unit price is positive (> 0).
        Transmits only product_name and unit_price using exclude_unset=True.
    """
    print("\n" + "=" * 40)
    print(f"        EDIT PRODUCT: {product_data.product_name}")
    print("=" * 40)

    # 1. User Input for Product Name
    raw_name = input(f"Enter New Product Name (Press Enter to keep '{product_data.product_name}'): ").strip()
    new_name = raw_name if raw_name else product_data.product_name

    # 2. User Input for Unit Price
    raw_price = input(f"Enter New Unit Price (Press Enter to keep {product_data.unit_price}): ").strip()
    if raw_price:
        try:
            new_price = float(raw_price)
            if new_price <= 0:
                print("\n[INPUT ERROR] Unit price must be greater than zero.")
                return
        except ValueError:
            print("\n[INPUT ERROR] Please enter a valid number for unit price.")
            return
    else:
        new_price = product_data.unit_price

    # 3. Create update schema with name and unit price only (stock_quantity excluded)
    update_data = ProductUpdate(
        product_name=new_name,
        unit_price=new_price
    )
    payload = update_data.model_dump(exclude_unset=True)

    # 4. Transmit PATCH request to backend
    try:
        url = f"{my_merchant.url}/products/{product_data.id}/edit"
        response = httpx.patch(url, json=payload, timeout=5.0)

        if response.status_code == 200:
            product_data.product_name = new_name
            product_data.unit_price = new_price
            print(f"\n[SUCCESS] Product successfully updated!")
            print(f"Name: {product_data.product_name} | Price: {product_data.unit_price:.2f} | Stock: {product_data.stock_quantity}")
        else:
            print(f"\n[API ERROR {response.status_code}]: {response.text}")

    except httpx.RequestError as e:
        print(f"\n[API ERROR] Could not connect to API server: {e}")

def merchant_interface(current_merchant: MerchantResponse) -> None:
    """
    Description / Purpose:
        Main CLI loop controlling merchant operations including inventory management and settings.

    Args / Parameters:
        current_merchant (MerchantResponse): Currently authenticated merchant session object.

    Returns:
        None.

    Constraints / Notes:
        Exits loop and terminates session when settings logout returns True.
    """
    my_merchant = MerchantInterface(current_merchant)
    print(my_merchant.welcome_message())
    print(f"Store Name: {my_merchant.current_merchant.store_name}")

    while True:
        merchant_menu()
        choice = input("Select an option (1-5): ").strip()

        match choice:
            case "1":
                add_product_flow(my_merchant)
            case "2":
                print("\n[Action] Update Stock selected.")
                try:
                    all_products = display_all_products(my_merchant)
                    if not all_products:
                        continue

                    select_product = input("Enter Product ID: ").strip()

                    response = httpx.get(f"{my_merchant.url}/products/{select_product}", timeout=5.0)

                    if response.status_code == 200:
                        payload = response.json()
                        product_data = ProductResponse(**payload)
                        update_stock_flow(my_merchant, product_data)
                    elif response.status_code == 404:
                        error_detail = response.json().get("detail", "Product not found.")
                        print(f"\n[NOT FOUND] {error_detail}")

                except httpx.RequestError as e:
                   print(f"\n[ERROR] Could not connect to API server: {e}")
            case "3":
                print("\n[Action] Edit Stock selected.")
                all_products = display_all_products(my_merchant)
                if not all_products:
                    continue

                edit_product_id = input("Enter Product ID: ").strip()
                response = httpx.get(f"{my_merchant.url}/products/{edit_product_id}", timeout=5.0)

                if response.status_code == 200:
                    payload = response.json()
                    edit_stock_flow(my_merchant, ProductResponse(**payload))
                elif response.status_code == 404:
                    error_detail = response.json().get("detail", "Product not found.")
                    print(f"\n[NOT FOUND] {error_detail}")
            case "4":
                print("\n[Action] Delete Stock selected.")
                all_products = display_all_products(my_merchant)
                if not all_products:
                    continue
                delete_product_id = input("Enter Product ID: ").strip()
                delete_stock_flow(delete_product_id, my_merchant)
            case "5":
                should_logout = handle_settings(my_merchant)
                if should_logout:
                    break
            case _:
                print("\n[ERROR] Invalid option. Please select 1-5.")
