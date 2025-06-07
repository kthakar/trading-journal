from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_entries():
    return {"entries": []}

@router.post("/")
def create_entry():
    return {"id": str(uuid4()), "created_at": datetime.utcnow()}

@router.put("/{entry_id}")
def update_entry(entry_id: str):
    return {"id": entry_id, "updated": True}

@router.delete("/{entry_id}")
def delete_entry(entry_id: str):
    return {"id": entry_id, "deleted": True}

@router.get("/calendar")
def journal_calendar():
    return {"entries": []}

@router.get("/search")
def journal_search():
    return {"results": []}
