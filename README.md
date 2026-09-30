# Order Management System

A learning-focused backend application for managing customers, merchants, products, cart items, and orders with FastAPI and Pydantic v2.

The project is designed to practice layered architecture, API validation, ownership checks, and CLI-to-API integration in a realistic e-commerce workflow.

---

## Overview

This repository currently includes:

- Customer registration and account management
- Merchant registration and product inventory flows
- Authentication for customer and merchant users
- Cart operations and checkout logic
- Order history and ownership validation
- JSON-backed persistence for local prototype data
- A terminal-based interface that calls the backend through HTTP

The implementation is intentionally structured as a hands-on backend project rather than a production-grade SaaS system.

---

## Tech Stack

- Python 3.14+
- FastAPI
- Pydantic v2
- Uvicorn
- HTTPX
- python-dotenv

---

## Current Architecture

```text
.
├── main.py                           # Starts the API server and launches the CLI interface
├── pyproject.toml                    # Project metadata and dependencies
├── README.md                        # Project overview and setup instructions
├── src/
│   └── backend/
│       ├── app.py                   # FastAPI app assembly and router registration
│       ├── dependencies.py          # Shared API base URL, service access, and ownership dependencies
│       ├── utilities.py             # Shared configuration helper values
│       ├── controller/
│       │   ├── AuthenticationController.py
│       │   ├── CartController.py
│       │   ├── CustomerController.py
│       │   ├── MerchantController.py
│       │   └── OrderController.py
│       ├── database/
│       │   ├── cart.json
│       │   ├── customer.json
│       │   ├── merchant.json
│       │   ├── order.json
│       │   └── product.json
│       ├── interface/
│       │   ├── app_interface.py
│       │   ├── customer_interface.py
│       │   ├── handle_order_interface.py
│       │   ├── handle_user.py
│       │   └── merchant_interface.py
│       ├── repository/
│       │   └── repositories.py
│       ├── schemas/
│       │   ├── Cart.py
│       │   ├── Order.py
│       │   ├── OrderItems.py
│       │   ├── Product.py
│       │   └── Users/
│       │       ├── Customer.py
│       │       ├── Merchant.py
│       │       └── User.py
│       └── service/
│           ├── authentication_service.py
│           ├── customer_service.py
│           ├── merchant_services.py
│           ├── order_service.py
│           └── user_service.py
```

---

## Key Features

### Customer flow
- Register as a customer
- Log in and maintain an active session
- View merchant stores and product listings
- Access personal profile details
- Update only editable customer fields
- Restrict access by customer ownership

### Merchant flow
- Register as a merchant
- Log in with merchant credentials
- Create, edit, and delete products
- Manage merchant profile information
- Protect mutations with ownership validation

### Shopping flow
- Add items to cart
- Modify or remove cart entries
- Check out to create an order
- Review order history for the active customer

### Ownership and validation patterns
- Active user IDs are resolved from the current session
- Route dependencies verify that a customer or merchant can only access their own records
- Pydantic schemas validate payloads before storage or updates
- Service logic saves changes to the JSON repository layer

---

## Running the Project

### Prerequisites

- Python 3.14+
- Optional: uv for dependency management

### Option 1: Standard install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Option 2: Using uv

```bash
uv sync
```

### Start the app

```bash
python main.py
```

This starts:
- the FastAPI server in the background
- the interactive terminal interface for the order system

The app currently runs on:

- http://127.0.0.1:8001

---

## API Access

When the server is running, FastAPI exposes Swagger docs at:

- http://127.0.0.1:8001/docs

The app registers separate routers for:

- customer routes
- merchant routes
- authentication routes
- cart routes
- order routes

---

## Notes on Current State

This codebase is a strong learning project for backend and API design, but it is not yet a production authentication system.

The current implementation uses local session state and JSON repository storage. That makes it easy to understand and debug, and it matches the learning goals of the project, but for real multi-user deployment you would replace this with:

- JWT or session-based identity management
- database-backed persistence instead of JSON files
- better password hashing and security checks
- a proper production deployment setup

---

## Learning Goals

This project is focused on consolidating skills in:

- REST API design with FastAPI
- Pydantic v2 validation and schema modeling
- dependency injection and route-level authorization
- separation of concerns between controller, service, and repository layers
- CLI-to-API communication using HTTP clients
- e-commerce workflows for order and inventory management

---

## Summary

The repository is a practical FastAPI order-management backend that demonstrates end-to-end application flow from registration and authentication through cart, order, and merchant operations. It is especially useful for learning architecture, validation, and ownership logic in a realistic domain model.
