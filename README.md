# Trading Journal

This repository contains documentation and backend implementation for the Trade Blotter application.

## Backend Setup

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Copy the environment file and adjust as needed:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Set your Tastytrade credentials in `backend/.env` if you plan to use the
   Tastytrade integration. This requires `TASTY_CLIENT_ID`,
   `TASTY_CLIENT_SECRET`, and a long-lived `TASTY_REFRESH_TOKEN` obtained using
   the OAuth2 authorization code flow.
3. Run the API server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. A health check endpoint is provided at `/health`.

## Additional Documentation
- [Technical Design Document](docs/TDD.md) – includes the trade pipeline algorithm
