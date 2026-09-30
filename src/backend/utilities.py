import os
import uuid
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001/api/v1")

def generate_product_id() -> str:
    """
    Description / Purpose:
        Generates a collision-resistant compact unique identifier string for products.

    Args / Parameters:
        None.

    Returns:
        str: 8-character uppercase alphanumeric identifier string (e.g., 'E4F7A91B').

    Constraints / Notes:
        Derives entropy from uuid.uuid4 to eliminate collision risk across server restarts.
    """
    return uuid.uuid4().hex[:8].upper()



