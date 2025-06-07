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
3. Run the API server:
   ```bash
   uvicorn backend.app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. A health check endpoint is provided at `/health`.
