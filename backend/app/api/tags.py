from uuid import uuid4
from fastapi import APIRouter

router = APIRouter()

tags_store = {}

@router.get("/")
def list_tags():
    return {"tags": list(tags_store.values())}

@router.post("/")
def create_tag(name: str):
    tag_id = str(uuid4())
    tag = {"id": tag_id, "name": name}
    tags_store[tag_id] = tag
    return tag

@router.put("/{tag_id}")
def update_tag(tag_id: str, name: str):
    tag = tags_store.get(tag_id, {"id": tag_id})
    tag["name"] = name
    tags_store[tag_id] = tag
    return tag

@router.delete("/{tag_id}")
def delete_tag(tag_id: str):
    tags_store.pop(tag_id, None)
    return {"id": tag_id, "deleted": True}
