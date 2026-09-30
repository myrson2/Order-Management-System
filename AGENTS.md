# 🤖 Project Background & Agent Context

> ⚠️ **MANDATORY AGENT DIRECTIVE:** All AI agents operating within this repository **MUST ALWAYS** read, inspect, and strictly adhere to all instructions, rules, and guidelines located inside the `.agents/` directory (specifically `.agents/rules.md`) before taking any action.
> 
> 🌿 **BRANCH-SCOPED REVIEW DIRECTIVE:** When instructed to "check" or "check for bugs" (e.g., "check for this branch only"), agents must strictly evaluate only the changes and files modified within the current working branch relative to `main`.

---

## 📌 Project Overview
This repository is an **Order and Inventory Management System** built with **FastAPI**, **Pydantic v2**, and **Python**. It serves as an active, hands-on learning codebase designed to bridge foundational Python programming with professional web backend and fullstack development.

---

## 🎯 Primary Purpose
* **FastAPI Core Mastery:** Understanding RESTful API design, controller routing, request/response lifecycle, and dependency injection.
* **Pydantic Schemas & Data Validation:** Mastering strict type safety, data modeling, request payload validation, custom field validators, and JSON serialization (`model_dump(mode='json')`).
* **Clean Layered Architecture:** Practicing separation of concerns across Schemas, Repositories (JSON file storage), Services (business logic & caching), Controllers (API routing), and Interfaces (HTTP CLI client via `httpx`).

---

## 🚀 Future Roadmap & Development Roadmap
As the codebase evolves towards a production-ready **Fullstack Application**, future developments will focus on:

1. **Relational Database & ORM Integration:** Transitioning from JSON file storage to **SQL** (PostgreSQL / SQLite via SQLAlchemy or SQLModel).
2. **Asynchronous Programming:** Leveraging native `async` / `await` paradigms across database queries, HTTP clients, and background tasks.
3. **Security & Authentication:** Implementing JWT authentication, password hashing (Passlib/Bcrypt), OAuth2, role-based authorization (RBAC), and CORS security middleware.
4. **Fullstack Frontend:** Building a modern interactive frontend (React, Vue, or Next.js) that consumes the FastAPI REST API endpoints.

---

## 🌿 Branch-Scoped Review Rule
* Whenever the user asks to "check", "check the refactored areas", or "check for bugs" (e.g., "check for this branch only"):
  * AI agents must scope and restrict all analysis, code reviews, and bug checking **strictly to the current branch** and files modified relative to `main`.
  * Do not audit or review unrelated legacy files or other branches unless explicitly directed.

