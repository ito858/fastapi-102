# Membership System Setup Instructions

## Prerequisites
- MySQL database set up with a 'users' table (id, username, password).
- uv installed (https://github.com/astral-sh/uv).

## Configuration
1. Edit `backend/.env` with your MySQL credentials:
   - Copy `backend/.env.template` to `backend/.env`.
   - Replace placeholders (<username>, <password>, <host>, <database>) with your actual values.

## Running the Backend
1. Navigate to the backend directory:
   ```bash
   cd membership_system_uv/backend
   ```
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Start the FastAPI server:
   ```bash
   uv run fastapi dev main.py
   ```

## Running the Frontend
1. Navigate to the frontend directory:
   ```bash
   cd membership_system_uv/frontend
   ```
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Start the Streamlit app:
   ```bash
   uv run streamlit run app.py
   ```

## Access
- Backend API: http://127.0.0.1:8000
- Frontend UI: http://localhost:8501
