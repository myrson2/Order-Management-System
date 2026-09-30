from backend.interface import merchant_interface
from backend.interface import customer_interface
from backend.interface.handle_user import UserInterface
from backend.interface.merchant_interface import MerchantInterface
from backend.schemas.Users import MerchantResponse, CustomerResponse
from backend.utilities import API_BASE_URL

CUSTOMER_URL = f"{API_BASE_URL}/customer"
MERCHANT_URL = f"{API_BASE_URL}/merchant"
user_interface = UserInterface(CUSTOMER_URL, MERCHANT_URL)

def menu() -> None: 
    """
    Description / Purpose:
        Displays the main unauthenticated terminal menu options (Login, Register, Exit).

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Prints formatted ASCII menu to terminal.
    """
    print("\n" + "=" * 40)
    print("   ORDER MANAGEMENT SYSTEM (API BASED SYSTEM)")
    print("=" * 40)

    print("1. Login")
    print("2. Register New Account")
    print("3. Exit")
    print("=" * 40)

def order_menu() -> None:
    """
    Description / Purpose:
        Displays the logged-in user menu options (Open Customer Menu, Edit Account, Logout).

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Only presented when current_user session is active.
    """
    print("1. Open Customer Management Menu")
    print("2. Edit Account")
    print("3. Logout")
    print("=" * 40)

def main_interface() -> None:
    """
    Description / Purpose:
        Main CLI loop controlling state transitions between logged-out and logged-in user sessions.

    Args / Parameters:
        None.

    Returns:
        None.

    Constraints / Notes:
        Runs infinite loop until user selects exit choice (3). Communicates with FastAPI via httpx.
    """
    current_user = None  # Holds logged-in customer session data

    while True:
        # STATE 1: NOT LOGGED IN
        if current_user is None:
            menu()
            choice = input("Select option (1-3): ").strip()

            match choice:
                case "1": # Login 
                    while current_user is None:
                        current_user = user_interface.user_authentication()
                        if current_user is not None:
                            break

                        is_continue = input('Try again? [Y/N]: ').strip().upper()
                        if is_continue == "Y":
                            continue
                        elif is_continue == "N":
                            break
                case "2": # Register 
                    user_interface.account_registration()
                case "3":
                    print("\nExiting System. Goodbye!")
                    break
                case _:
                    print("\n[ERROR] Invalid choice. Enter 1-3.")
        else:
            if current_user is None:
                return None

            if isinstance(current_user, MerchantResponse):
                merchant_interface.merchant_interface(current_user)
            elif isinstance(current_user, CustomerResponse):
                customer_interface.customer_interface(current_user)

            current_user = None


if __name__ == "__main__":
    main_interface()