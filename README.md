# Waste Sorting & Recycling Optimization API

## Project Overview
This project implements a **Waste Sorting & Recycling Optimization API** supporting:
1.  **Barbecha Onboarding & Fair-Payment Ledger**: Registration and transaction logging for informal collectors with JWT authentication.
2.  **Citizen Assistant**: "Where do I drop this?" search and drop-off point locator.

## Tech Stack
-   **Backend**: Python, FastAPI
-   **Database**: SQLite (SQLAlchemy ORM)
-   **Authentication**: JWT (python-jose, passlib)
-   **Validation**: Pydantic
-   **Containerization**: Docker
-   **Documentation**: Swagger UI (Auto-generated)
-   **Frontend**: Enhanced HTML/JS with tabs and authentication

## Setup & Running

### Option 1: Using Docker (Recommended)
1.  Navigate to the project directory:
    ```bash
    cd waste-recycling-api
    ```
2.  Build and Run:
    ```bash
    docker-compose up --build
    ```
3.  Access the API:
    -   **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    -   **Frontend Demo**: Open `frontend/index.html` in your browser.

### Option 2: Local Python Setup (Using start.bat)
1.  Double-click `start.bat` in the project folder (it creates venv, installs deps, runs server).
2.  Or manually:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

## API Endpoints
-   **Auth**: `POST /collectors/` (register), `POST /collectors/token` (login)
-   **Collectors**: `GET /collectors/me`, `POST /collectors/transaction`, `GET /collectors/history`
-   **Citizens**: `GET /citizen/items`, `GET /citizen/drop-off-points`

## Testing & Simulation for Presentation

### 1. API Endpoints
-   Use **Insomnia** or the **Swagger UI** (`/docs`) to test endpoints.
-   Register a user, login to get JWT, then access protected endpoints.

### 2. Check Logs (Flags)
Logs are stored in `logs/app.log`.
To check logs in Docker:
```bash
docker-compose logs -f
```

### 3. Error Catalogue (PARSEL)
Common errors handled:
-   `400 Bad Request`: "Username already registered".
-   `401 Unauthorized`: Invalid credentials or missing token.
-   `404 Not Found`: Collector ID invalid.

## Project Structure
-   `app/routers/collectors.py`: Barbecha endpoints with JWT.
-   `app/routers/citizen.py`: Citizen search endpoints.
-   `app/models.py`: Database models.
-   `app/auth.py`: JWT utilities.
-   `logs/app.log`: Application log files.
-   `frontend/index.html`: Enhanced UI with auth and tabs.
-   `start.bat`: Manual start script for local testing.
-   `prompt_history.md`: History of Copilot prompts used.

## Additional Features Added
-   JWT Authentication for secure access.
-   Login/Register functionality.
-   Improved UI with tabs, history view, and better styling.
-   Manual start batch for easy local testing.
-   Prompt history documentation as required.