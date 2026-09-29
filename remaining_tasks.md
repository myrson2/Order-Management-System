# 📋 Remaining Tasks & Project Checklist

**Project:** Order and Inventory Management System (FastAPI Backend + CLI Interface)  
**Overall Completion Status:** 🟢 **~86% Completed**  
**Date:** September 23, 2026  

---

## 📊 Module Status Overview

```text
[████████████████████████░░░░] 86% Completed
```

| Module | Status | Completion % |
| :--- | :--- | :---: |
| **Merchant & Inventory Management** | 🟢 Complete | 95% |
| **User Authentication & Schemas** | 🟢 Complete | 95% |
| **Customer Shopping Experience (CLI)** | 🟢 Complete | 90% |
| **Cart Persistence & PATCH Editing** | 🟢 Complete | 90% |
| **Order Management & Checkout Backend** | 🟡 In Progress | 30% |
| **Automated Testing (pytest)** | ⏳ Deferred | 0% |

---

## 🎯 High-Priority Remaining Work (To Reach 100%)

### 📦 Phase 1: Order Placement & Checkout Backend (Current Milestone)

#### 1. Database & Persistence Layer (`src/backend/database/order.json`)
- [ ] Initialize `src/backend/database/order.json` file for persistent order storage.
- [ ] Implement `OrderRepository` in `src/backend/repository/repositories.py` inheriting from `Repository(ABC)`:
  - `save_repo(data: list[dict]) -> None`: Write completed orders to `order.json`.
  - `load_repo() -> list[dict]`: Read persistent orders from `order.json`.

#### 2. Service Layer Logic (`src/backend/service/order_service.py`)
- [ ] Implement `checkout_order(customer_id: str)` business logic:
  - Retrieve all active cart items for `customer_id` from `cart_cache`.
  - Validate that requested quantities do not exceed available stock in `product.json`.
  - Generate a new `Order` model instance with a unique UUID (`id`).
  - Convert each cart item into an `OrderItem` schema (`order_item_id`, `product_id`, `quantity`, `unit_price`, `total_price`).
  - Deduct purchased item quantities from `product.json` stock counts.
  - Append the completed `Order` payload to `order_cache` and save to `order.json`.
  - Clear the customer's items from `cart_cache` and update `cart.json`.
- [ ] Implement `get_order_history(customer_id: str)` business logic:
  - Filter `order_cache` records matching `customer_id`.

#### 3. Controller Endpoints (`src/backend/controller/OrderController.py`)
- [ ] Create `OrderController.py` and register router in `src/backend/app.py`:
  - `POST /api/v1/order/checkout/{customer_id}` (`HTTP 201 Created`): Process checkout payload and return created `Order`.
  - `GET /api/v1/order/customer/{customer_id}` (`HTTP 200 OK`): Retrieve past order receipts for the customer.

#### 4. CLI Client Integration (`src/backend/interface/customer_interface.py`)
- [ ] Wire up **Checkout** (`store_menu` Option 4):
  - Call `POST /api/v1/order/checkout/{customer_id}` via `httpx`.
  - Display formatted receipt details (Order ID, Items, Total Price) upon success.
- [ ] Wire up **History** (`customer_menu` Option 3):
  - Call `GET /api/v1/order/customer/{customer_id}` via `httpx`.
  - Print formatted past order receipts.

---

### 🔑 Phase 2: Profile & Security Enhancements (Optional Polish)

- [ ] **Uncomment & Implement Customer Profile Editing:**
  - Re-enable `@router.patch("/{customer_id}")` in `CustomerController.py` to allow updating customer contact details.
- [ ] **Password Hashing:**
  - Hash stored plaintext passwords in `merchant.json` and `customer.json` using `bcrypt` / `passlib`.

---

### 🧪 Phase 3: Automated Test Suite (Deferred Learning Phase)

- [ ] Configure `pytest` runner in `pyproject.toml`.
- [ ] Write schema validation tests (`Product`, `Customer`, `Cart`, `Order`).
- [ ] Write service unit tests and BOLA security isolation tests.
- [ ] Write FastAPI `TestClient` API integration tests.

---

## 💡 Recommended Next Action
Begin **Phase 1, Task 1 & 2**: Initialize `order.json`, create `OrderRepository`, and write the `checkout_order()` method in `OrderService.py`!
