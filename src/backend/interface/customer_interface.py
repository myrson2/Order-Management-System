import httpx

from backend.schemas.Cart import CartCreate, CartResponse, CartUpdate
from backend.schemas.Product import ProductResponse
from backend.schemas.Users import CustomerResponse, MerchantResponse
from backend.service.customer_service import CustomerService
from backend.utilities import API_BASE_URL

class CustomerInterface:
    """CLI client interface handler for Customer operations."""
    
    def __init__(self, current_customer: CustomerResponse):
        """
        Initializes CustomerInterface with active session data and base URL.
        Sets up an empty in-memory cart.
        """
        self.current_customer = current_customer
        self.base_url = API_BASE_URL
        self.customer_url = f"{self.base_url}/customer/{current_customer.id}"

    def welcome_message(self) -> str:
        """Returns a formatted welcome string."""
        return f"\nLogged in as: {self.current_customer.first_name} {self.current_customer.last_name} ({self.current_customer.email}) | Rewards: ${self.current_customer.rewards:.2f}"

def display_stores(curr_customer: CustomerInterface) -> list[dict]:
    """Fetches and displays all registered merchants (stores)."""
    try:
        return CustomerService.get_stores()
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")
        return []

def display_store_items(curr_customer: CustomerInterface, store_name: str) -> None:
    """Fetches and displays available products for a specific merchant."""
    try:
        products = CustomerService.get_store_products(store_name)
        if not products:
            print('Doesnt Have Products')
            return
        print("\n--- AVAILABLE PRODUCTS ---")
        for product in products:
            name = product.get('product_name', 'Unknown')
            price = product.get('unit_price', 0.0)
            stock = product.get('stock_quantity', 0)
            product_id = product.get('id')
            print(f"Product_ID: {product_id} | Product: {name} | Price: ${price:.2f} | Stock: {stock}")
        print("--------------------------\n")
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def store_menu() -> None:
    """Displays the interactive menu inside a store."""
    print("\n" + "=" * 40)
    print("             STORE MENU                 ")
    print("=" * 40)
    print("1. Add To Cart")
    print("2. View Cart")
    print("3. Edit Cart Item")
    print("4. Delete Cart Item")
    print("5. Checkout")
    print("6. Exit Store")
    print("=" * 40)

def get_product_response(prd_id: str, customer: CustomerInterface, merchant: MerchantResponse):
    """Return a validated product from the customer cart API."""
    return CustomerService.get_product(
        str(customer.current_customer.id), prd_id, str(merchant.id)
    )

def add_to_cart(customer: CustomerInterface, merchant: MerchantResponse) -> CartResponse | None:
    """
    Description / Purpose:
        CLI interactive prompt collecting Product ID and quantity to submit a new cart item to the backend API.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.
        merchant (MerchantResponse): MerchantResponse schema instance representing the selected store.

    Returns:
        CartResponse | None: CartResponse object upon successful API creation, or None on failure.

    Constraints / Notes:
        Sends HTTP POST request to /cart/customer/{customer_id}/add using httpx.
    """
    try:
        #make validation for prd_id if that id is there or not
        prd_id = input("\nEnter Product ID: ").strip()

        product = get_product_response(
            prd_id=prd_id,
            customer=customer,
            merchant=merchant
        )

        qty = int(input("\nEnter Quantity: "))

        if qty > product.stock_quantity:
            raise ValueError(f'Order items cannot exceed available stock ({product.stock_quantity}).')

        prd_items = CartCreate(
            product_name=product.product_name,
            customer_id=str(customer.current_customer.id),
            merchant_id=str(merchant.id),
            product_id=prd_id,
            quantity=qty
        )

        cart_item = CustomerService.add_cart_item(prd_items)
        print('Customer Added An Item Successfully.')
        return cart_item
    except ValueError as e:
        print(e)
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def view_cart(customer: CustomerInterface) -> None:
    """
    Description / Purpose:
        Fetches and displays active cart items for the logged-in customer from the backend API.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        None.

    Constraints / Notes:
        Sends HTTP GET request to /cart/customer/{customer_id}/view and formats output to terminal.
    """
    try:
        cart_items = CustomerService.get_cart(str(customer.current_customer.id))
        if not cart_items:
            print("\n[INFO] Your shopping cart is empty.")
            return
        print("\n--- YOUR CART ---")
        for item in cart_items:
            cart_id = item.get('id', 'N/A')
            product_name = item.get('product_name', 'Unknown Product')
            product_id = item.get('product_id', 'N/A')
            merchant_id = item.get('merchant_id', 'N/A')
            quantity = item.get('quantity', 0)
            print(f"Cart ID: {cart_id} | Product: {product_name} ({product_id}) | Store ID: {merchant_id} | Quantity: {quantity}")
        print("-----------------\n")
    except httpx.HTTPError as error:
        print(f"\n[API ERROR] Could not retrieve cart: {error}")

def edit_cart(customer: CustomerInterface) -> None:
    """
    Description / Purpose:
        CLI interactive prompt allowing a customer to edit quantities of an existing cart item.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.
        merchant (MerchantResponse): MerchantResponse schema instance representing the store.

    Returns:
        None.

    Constraints / Notes:
        Sends HTTP PATCH request to /cart/customer/{customer_id}/item/{cart_id} with CartUpdate payload.
    """
    try:
        view_cart(customer)
        cart_id = input("\nEnter Cart Item ID to edit: ").strip()

        customer_id = str(customer.current_customer.id)
        CustomerService.get_cart_item(customer_id, cart_id)
        edit_qty = int(input("Enter New Quantity: ").strip())
        update_payload = CartUpdate(quantity=edit_qty)
        CustomerService.update_cart_item(customer_id, cart_id, update_payload)
        print("\n[SUCCESS] Cart item updated successfully!")
    except ValueError:
        print("\n[INPUT ERROR] Please enter a valid number for quantity.")
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def delete_cart_item_cli(customer: CustomerInterface) -> None:
    """
    Description / Purpose:
        CLI interactive prompt requesting a Cart Item ID to issue an HTTP DELETE request to the backend.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        None.

    Constraints / Notes:
        Sends HTTP DELETE request to /cart/customer/{customer_id}/{cart_id} using httpx.
    """
    try:
        view_cart(customer)
        cart_id = input("\nEnter Cart Item ID to delete: ").strip()

        CustomerService.delete_cart_item(str(customer.current_customer.id), cart_id)
        print(f"\n[SUCCESS] Cart item ({cart_id}) deleted successfully!")
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def checkout_cli(customer: CustomerInterface) -> None:
    """
    Description / Purpose:
        CLI interactive prompt displaying current cart items, requesting checkout confirmation, and issuing an HTTP POST request to process the order receipt.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        None.

    Constraints / Notes:
        Sends HTTP POST request to /order/checkout/{customer_id} using httpx.
    """
    try:
        view_cart(customer)
        confirm = input("\nConfirm Checkout? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\n[INFO] Checkout cancelled.")
            return

        order_data = CustomerService.checkout(str(customer.current_customer.id)).model_dump(mode='json')
        print("\n" + "=" * 50)
        print("             ORDER RECEIPT (SUCCESS)            ")
        print("=" * 50)
        print(f"Order ID: {order_data.get('id')}")
        print(f"Order Date: {order_data.get('order_date')}")
        print("Items Purchased:")
        for item in order_data.get('order_list', []):
            print(f"  - {item.get('product_name')} (x{item.get('quantity')}) @ ${item.get('unit_price'):.2f} = ${item.get('total_price'):.2f}")
        print(f"Total Amount Paid: ${order_data.get('total_amount'):.2f}")
        print("=" * 50 + "\n")
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def view_order_history_cli(customer: CustomerInterface) -> None:
    """
    Description / Purpose:
        Fetches and displays past completed order receipts for the logged-in customer from the backend API.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        None.

    Constraints / Notes:
        Sends HTTP GET request to /order/customer/{customer_id} using httpx.
    """
    try:
        history = CustomerService.get_order_history(str(customer.current_customer.id))
        if not history:
            print("\n[INFO] You have no past order receipts.")
            return
        print("\n" + "=" * 50)
        print("             PAST ORDER HISTORY                 ")
        print("=" * 50)
        for order in history:
            print(f"\nOrder ID: {order.get('id')} | Date: {order.get('order_date')} | Total: ${order.get('total_amount'):.2f}")
            print("  Items:")
            for item in order.get('order_list', []):
                print(f"    - {item.get('product_name')} x{item.get('quantity')} (${item.get('total_price'):.2f})")
        print("=" * 50 + "\n")
    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Network failed: {e}")

def handle_store_shopping(customer: CustomerInterface, store_name: str) -> None:
    """
    Handles the shopping flow inside a specific store:
    - Add To Cart
    - View Cart
    - Edit Order
    - Delete Cart Item
    - Checkout
    """

    # Get merchant object using store name
    try:
        merchant_res = CustomerService.get_merchant(store_name)
        if merchant_res is not None:
            display_store_items(customer, store_name)  # Change Store name to Merchant Object
            while True:
                store_menu()
                choice = input("Select an option (1-6): ").strip()

                match choice:
                    case "1":
                        print("\n[Action] Add To Cart selected.")
                        add_to_cart(customer, merchant_res)
                    case "2":
                        print("\n[Action] View Cart selected.")
                        view_cart(customer)
                    case "3":
                        print("\n[Action] Edit Cart Item selected.")
                        edit_cart(customer)
                    case "4":
                        print("\n[Action] Delete Cart Item selected.")
                        delete_cart_item_cli(customer)
                    case "5":
                        print("\n[Action] Checkout selected.")
                        checkout_cli(customer)
                    case "6":
                        print("\nReturning to Customer Management Menu...")
                        break
                    case _:
                        print("\n[ERROR] Invalid option. Please enter 1-6.")
        else:
            return None
    except httpx.HTTPError as e:
        print(e)

def customer_menu() -> None:
    """Displays the main Customer Management Menu."""
    print("\n" + "=" * 40)
    print("        CUSTOMER MANAGEMENT MENU        ")
    print("=" * 40)
    print("1. View/Choose Stores")
    print('2. View Cart')
    print("3. History")
    print("4. Logout")
    print("=" * 40)

def logout(customer: CustomerInterface) -> bool:
    """
    Description / Purpose:
        Sends an HTTP POST request to terminate the active customer authentication session.

    Args / Parameters:
        customer (CustomerInterface): Active customer session interface instance.

    Returns:
        bool: True if logout succeeds (HTTP 200), False otherwise.

    Constraints / Notes:
        Sends customer profile payload to /auth/logout endpoint.
    """
    try:
        is_logged_out = CustomerService.logout_customer(customer.current_customer)
        print(f"\n[LOGOUT] Logging out {customer.current_customer.first_name} {customer.current_customer.last_name}...")

        if is_logged_out:
            print(
                f"\n[LOGOUT] Successfully logged out {customer.current_customer.first_name} {customer.current_customer.last_name}.")
            return True
        else:
            print("\n[ERROR] Logout failed.")
            return False

    except httpx.HTTPError as e:
        print(f"\n[API ERROR] Could not connect to server for logout: {e}")
        return False

def customer_interface(current_customer: CustomerResponse) -> None:
    """
    Main CLI loop for the Customer.
    Handles:
    - View/Choose Stores
    - View Cart
    - History
    - Logout
    """
    customer = CustomerInterface(current_customer)
    print(customer.welcome_message())
    
    while True:
        customer_menu()
        choice = input("Select an option (1-4): ").strip()
        
        match choice:
            case "1":
                print("\n[Action] View/Choose Stores selected.")
                stores = display_stores(customer)

                if stores is None or len(stores) == 0:
                    print('Dont have any stores available.')
                else:
                    for store in stores:
                        print(f"Store ID: {store.get('id')} | Name: {store.get('store_name')}")

                merchant_store = input("Enter store name: ")

                if any(str(store.get("store_name")) == merchant_store for store in stores):
                    handle_store_shopping(customer, merchant_store)
                else:
                    print("Invalid store name.")
            case '2':
                print("\n[Action] View Cart")
                view_cart(customer)

            case "3":
                print("\n[Action] History selected.")
                view_order_history_cli(customer)
            case "4":
                print("\nLogging out...")
                is_logging_out = logout(customer)

                if is_logging_out:
                    break
                else:
                    continue
            case _:
                print("\n[ERROR] Invalid option. Please enter 1-4.")
