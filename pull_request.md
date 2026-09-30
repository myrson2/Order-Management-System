# 🛒 Pull Request: Customer Profile, Shopping Cart & Checkout System

## 📌 Overview
This pull request implements the complete **Customer Profile**, **Shopping Cart**, and **Checkout Order Receipt System**. It introduces end-to-end functionality spanning all architectural layers (Controllers, Services, Repositories, Pydantic Schemas, and the Interactive CLI) to enable customers to register/login, browse product catalogs, manage shopping carts, and execute checkout transactions with real-time stock deduction and persistent receipt generation.

---

## 🚀 Key Features Implemented

### 1. Customer Management & Authentication
* **Registration & Profile Retrieval:** Added customer registration (`POST /api/v1/customer/create`) and profile lookup (`GET /api/v1/customer/{customer_id}`).
* **Repository & Storage:** Created `CustomerRepository` backed by `customer.json` with in-memory caching in `CustomerService`.

### 2. Shopping Cart System (RESTful API & Storage)
* **Cart Persistence:** Created `CartRepository` backed by `cart.json` to persist cart items between sessions.
* **Add to Cart (`POST /api/v1/cart/add_to_cart`):** Validates merchant stock availability prior to adding items to customer cart.
* **View Cart (`GET /api/v1/cart/my_cart/{customer_id}`):** Retrieves active cart items for the authenticated customer.
* **Update Cart Item (`PATCH /api/v1/cart/update_item/{customer_id}/{cart_id}`):** Performs partial updates (e.g. quantity adjustments) using Pydantic `exclude_unset=True`.
* **Delete Cart Item (`DELETE /api/v1/cart/delete_item/{customer_id}/{cart_id}`):** Removes individual items from customer cart.

### 3. Checkout Transaction & Order Receipt Pipeline
* **Persistent Order Repository:** Added `OrderRepository` backed by `order.json`.
* **5-Step Checkout Transaction (`POST /api/v1/order/checkout/{customer_id}`):**
  1. Validates that customer cart is not empty.
  2. Verifies inventory stock across store catalog for all line items.
  3. Deducts purchased quantities from merchant inventory (`product.json`).
  4. Generates immutable `Order` receipt with line item snapshots (`OrderItem`) and persists to `order.json`.
  5. Clears purchased items from `cart.json`.
* **Order History (`GET /api/v1/order/customer/{customer_id}`):** Allows customers to inspect previous purchase receipts.

### 4. Interactive Customer CLI Interface
* **Customer Session Flow:** Interactive login and registration CLI workflows.
* **Catalog Browsing:** Browse products by merchant with formatted ASCII tabular layouts.
* **Cart Operations:** Interactive cart viewing, quantity editing, and item removal.
* **Checkout Flow:** One-click checkout with a formatted ASCII order receipt display (itemized breakdown, quantities, unit prices, subtotal, and timestamp).
* **Order History View:** View historical order receipts directly in the terminal.

### 5. Architectural Standards & Clean Code
* **Pydantic v2 Type Safety:** Strict schemas (`Cart`, `Order`, `OrderItems`) utilizing `model_dump(mode='json')` serialization.
* **Dependency Injection:** Centralized repository and service factories in `dependencies.py`.
* **Docstring Standards:** Standardized 4-part docstrings (*Description / Purpose*, *Args / Parameters*, *Returns*, *Constraints / Notes*) across all functions and endpoints.

---

## 📂 Modified & Added Files Summary
* `src/backend/schemas/`: Added `Cart.py`, updated `Order.py` and `OrderItems.py`.
* `src/backend/repository/`: Added `CartRepository` and `OrderRepository` in `repositories.py`.
* `src/backend/service/`: Implemented cart logic and checkout transaction pipeline in `order_service.py`.
* `src/backend/controller/`: Added `CartController.py` and `OrderController.py`, registered in `app.py`.
* `src/backend/interface/`: Added `customer_interface.py` and linked to `handle_user.py`.

---

## 🚦 Verification & Merge Readiness
* **Merge Conflicts:** None. Verified against `origin/main` (clean fast-forward / 3-way merge).
* **Branch Status:** `CustomerProfile` is up to date with `origin/CustomerProfile`.
* **Status:** ✅ **Ready to Merge into `main`**.
