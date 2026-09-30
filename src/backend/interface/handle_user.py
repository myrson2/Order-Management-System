import httpx
from backend.schemas.Users import CustomerResponse, MerchantResponse
from backend.schemas.Users.Customer import CustomerCreate
from backend.schemas.Users.Merchant import MerchantCreate
from backend.schemas.Users.User import UserLogin, UserResponse
from pydantic import ValidationError
from backend.schemas.Users.User import EnumType
from backend.utilities import API_BASE_URL

class UserInterface:
    """CLI client interface handler for user authentication and account registration."""

    def __init__(self, customer_url: str, merchant_url: str):
        """
        Description / Purpose:
            Initializes UserInterface with target API endpoints for customer and merchant operations.

        Args / Parameters:
            customer_url (str): API endpoint URL for customer routes.
            merchant_url (str): API endpoint URL for merchant routes.

        Returns:
            None.

        Constraints / Notes:
            Stores URLs for HTTP client requests via httpx.
        """
        self.customer_url = customer_url
        self.merchant_url = merchant_url

    @staticmethod
    def user_authentication() -> UserResponse | None:
        """
        Description / Purpose:
            Prompts for credentials, queries API controller over HTTP, and verifies user login.

        Args / Parameters:
            None.

        Returns:
            UserResponse | None: Logged-in CustomerResponse/MerchantResponse object if authentication succeeds, or None.

        Constraints / Notes:
            Sends HTTP POST request to API backend and handles network/validation exceptions.
        """
        print("\n--- LOGIN ---")

        try:
            email = input("Enter Email (Format: @gmail.com): ").strip()
            password = input("Enter Password: ").strip()

            user_login = UserLogin(email=email, password=password)
            response = httpx.post(f"{API_BASE_URL}/auth/login", json=user_login.model_dump(mode="json"), timeout=5.0)

            if response.status_code == 200:
                user_dict = response.json()
                if user_dict.get("user_type") == EnumType.MERCHANT:
                    return MerchantResponse(**user_dict)
                return CustomerResponse(**user_dict)
            elif response.status_code in (401, 404):
                try:
                    error_detail = response.json().get("detail", "Invalid email or password.")
                except Exception:
                    error_detail = "Invalid email or password."
                print(f"\n[LOGIN FAILED] {error_detail}")
                return None
            else:
                print(f"\n[API ERROR {response.status_code}]: {response.text}")
                return None

        except ValidationError as e:
            for error in e.errors():
                field_name = error['loc'][0]
                error_message = error['msg'].replace("Value error, ", "")
                print(f"\n[ERROR] {field_name}: {error_message}")
            return None

        except httpx.RequestError:
            print("\n[API ERROR] Could not connect to server. Ensure FastAPI is running on http://127.0.0.1:8001")
            return None

    @staticmethod
    def account_registration():
        """
        Description / Purpose:
            Interactive CLI registration prompt collecting user details and submitting payloads to API backend.

        Args / Parameters:
            None.

        Returns:
            None.

        Constraints / Notes:
            Supports customer and merchant account types. Sends HTTP POST request over network via httpx.
        """
        print("\n--- REGISTER NEW ACCOUNT ---")
        data = None
        response = None

        try:
            loop = True
            while loop:
                try:
                    first_name = input("First Name: ").strip()
                    last_name = input("Last Name: ").strip()
                    email = input("Email: ").strip()
                    phone_num = input("Phone Number: ").strip()
                    pwd = input("Password (min 8 chars): ").strip()
                    u_type = input("User Type (Customer/Merchant): ").strip().lower()

                    match u_type:
                        case "merchant":
                            merchant_store_name = input("Merchant Store Name: ").strip()

                            data = MerchantCreate(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone_num,
                                password=pwd,
                                store_name=merchant_store_name
                            )
                            response = httpx.post(f"{API_BASE_URL}/auth/register/merchant", json=data.to_dict(), timeout=5.0)
                        case "customer":
                            data = CustomerCreate(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone_num,
                                password=pwd
                            )
                            response = httpx.post(f"{API_BASE_URL}/auth/register/customer", json=data.to_dict(), timeout=5.0)
                        case _:
                            raise ValueError(f"\n[ERROR]: User type ({u_type}) is not valid.")

                    loop = False

                except ValidationError as e:
                    print("\n[VALIDATION ERROR] Please fix the following errors and try again:")
                    for err in e.errors():
                        field = " -> ".join(str(loc) for loc in err.get("loc", []))
                        print(f" - {field.capitalize()}: {err.get('msg')}")
                    print() # Extra spacing before the loop restarts

            if data is None:
                raise ValueError("\n[ERROR] No data provided.")

            if response is None:
                raise ValueError("\n[ERROR] No response provided.")

            if response.status_code == 201:
                print(f"\n[API 201 SUCCESS] Account registered! You can now log in.")
            else:
                print(f"\n[API ERROR {response.status_code}]: {response.text}")
        except ValidationError as e:
            print(f"\n[ERROR] {e}")
        except httpx.ConnectError:
            print("\n[API ERROR] Could not connect to API server.")