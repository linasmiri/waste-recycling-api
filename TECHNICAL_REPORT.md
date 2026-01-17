# Waste Management & Recycling Optimization Platform
## Technical Documentation & Functional Specification

**Date:** January 17, 2026  
**Version:** 2.0.0  
**Status:** Alpha/Development  

---

## 1. Executive Summary
The **Waste Management & Recycling Optimization Platform** is a web-based solution designed to connect three key stakeholders in the waste management ecosystem: **Citizens**, **Collectors** (Barbechas), and **Administrators**. 

The system provides a public interface for citizens to learn about recycling, a secured workspace for collectors to track their collections and earnings, and a management dashboard for administrators to oversee the system's efficient operation.

---

## 2. Functional Requirements by Actor

### 2.1 Actor: Citizen (Guest User)
*Access Level: Public (No Authentication required)*

| Feature | Description |
| :--- | :--- |
| **Search Items** | Search for recyclable items by name or category (e.g., "Plastic", "Can"). |
| **View Instructions** | View specific recycling instructions and categorization for items. |
| **Browse Categories** | Filter items by material categories (Plastic, Metal, Glass, Paper, Electronics). |

### 2.2 Actor: Collector (Registered User)
*Access Level: Authenticated (JWT Token)*

| Feature | Description |
| :--- | :--- |
| **Registration** | Account creation with validation (Username, Full Name, Phone with `+216` check, Password) and Profile Image upload. |
| **Authentication** | Secure Login using OAuth2 (Username/Password) to receive an access token. |
| **Dashboard** | View real-time balance (TND), total weight collected, and recycling statistics. |
| **Declare Collection** | Record a new collection transaction by selecting a specific Item and entering the Weight (kg). Price is auto-calculated based on the item's rate. |
| **View History** | Access a chronological list of past collections with dates, items, weights, and earnings. |
| **Manage Profile** | Update personal information (Name, Phone) and upload a new profile picture. |

### 2.3 Actor: Administrator
*Access Level: Authenticated (Role: "admin")*

| Feature | Description |
| :--- | :--- |
| **Admin Dashboard** | View global statistics: Total Collectors, Total Weight Recycled, Total Revenue Generated, and Top Recycled Items. |
| **User Management** | View list of all collectors. Capability to **Edit** profiles, **Ban/Unban** users (toggle active status), and **Delete** accounts. |
| **Inventory Management** | **CRUD** (Create, Read, Update, Delete) operations for Recyclable Items. Admins set the price per kg and categories available to collectors. |

---

## 3. Technology Stack

### 3.1 Backend
*   **Framework:** **FastAPI** (Python 3.9+)
    *   chosen for high performance, automatic Swagger/OpenAPI documentation, and type safety.
*   **ORM:** **SQLAlchemy**
    *   Used for database abstraction and modeling.
*   **Data Validation:** **Pydantic**
    *   Ensures data integrity for requests (Schemas) and responses.
*   **Authentication:** 
    *   **OAuth2** with Password Flow.
    *   **JWT (JSON Web Tokens)** via `python-jose` for stateless authentication.
    *   **Passlib (Bcrypt)** for secure password hashing.

### 3.2 Frontend
*   **Core:** Vanilla **HTML5** & **JavaScript (ES6+)**.
*   **Styling:** **Tailwind CSS** (via CDN) for responsive, modern UI design.
*   **Communications:** Native Fetch API to communicate with the FastAPI backend.

### 3.3 Database
*   **Engine:** **SQLite** (default for development), extensible to PostgreSQL/MySQL.
*   **Structure:** Relational schema containing `collectors`, `recyclable_items`, `collections`, and `transactions`.

---

## 4. Key Dependencies & Libraries

Based on the `requirements.txt` and source code analysis:

```text
fastapi==0.109.0        # Web Framework
uvicorn==0.27.0         # ASGI Server
sqlalchemy==2.0.25      # Database ORM
pydantic==2.5.3         # Data Validation
python-jose[cryptography] # JWT Token handling
passlib[bcrypt]         # Password Hashing
python-multipart        # Form data & File Upload support
email-validator         # Email format validation
```

---

## 5. Deployment Architecture (Docker)

The application is containerized to ensure consistency across development and production environments.

### 5.1 Dockerfile Structure
The `Dockerfile` builds a lightweight Python environment:

```dockerfile
# Base Image
FROM python:3.9-slim

# Work Directory
WORKDIR /app

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code
COPY . .

# Static Files Volume (for profile images)
RUN mkdir -p /app/static/images

# Port Exposure
EXPOSE 8000

# Startup Command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Service Orchestration (docker-compose)
The `docker-compose.yml` orchestrates the service:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./waste_app.db:/app/waste_app.db  # Persist Database
      - ./static:/app/static              # Persist User Uploaded Images
      - ./logs:/app/logs                  # Persist Logs
    environment:
      - SECRET_KEY=your_production_secret_key
    restart: always
```

---

## 6. API Specification Highlights

### Authentication
*   `POST /collectors/login`: Exchange username/password for Bearer Token.
*   `POST /collectors/register`: Register new account (multipart/form-data for image).

### Collectors Scope
*   `GET /collectors/me`: Get current user profile.
*   `POST /collectors/collections`: Record a recycling transaction (Submits `item_id`, `weight`).
*   `GET /collectors/collections`: Get collection history.

### Admin Scope
*   `GET /admin/dashboard`: Aggregate system stats.
*   `GET /admin/collectors`: List all users.
*   `POST /admin/users/{id}/toggle-active`: Ban/Unban user.
*   `POST /admin/items`: Add new recyclable item definition.

### Public/Citizen Scope
*   `GET /citizen/items`: Search and list items.

---

## 7. Security Features
1.  **Password Hashing:** Passwords are never stored in plain text; Bcrypt is used with salt.
2.  **Role-Based Access Control (RBAC):** Middleware checks `user.role` (admin vs collector) before allowing access to sensitive endpoints.
3.  **CORS (Cross-Origin Resource Sharing):** Configured to allow frontend communication (currently `*` for dev, restrict in prod).
4.  **Input Validation:** Pydantic models prevent SQL injection and malformed data entry.

