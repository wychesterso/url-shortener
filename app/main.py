from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import uuid

app = FastAPI()
db: Dict[str, str] = {}

class URLItem(BaseModel):
    original_url: str

@app.post("/shorten")
def shorten_url(item: URLItem):
    short_id = uuid.uuid4().hex[:6]
    db[short_id] = item.original_url
    return {"short_url": f"https://localhost:8000/{short_id}"}

@app.get("/{short_id}")
def redirect_url(short_id: str):
    url = db.get(short_id)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"redirect_to": url}
