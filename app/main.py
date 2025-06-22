from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from app.database import Base, engine, SessionLocal, URL, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

class URLItem(BaseModel):
    original_url: str

@app.post("/shorten")
def shorten_url(item: URLItem, db: Session = Depends(get_db)):
    short_id = uuid.uuid4().hex[:6]
    db_url = URL(short_id=short_id, original_url=item.original_url)
    db.add(db_url)
    db.commit()
    return {"short_url": f"http://localhost:8000/{short_id}"}

@app.get("/{short_id}")
def redirect_url(short_id: str, db: Session = Depends(get_db)):
    db_url = db.query(URL).filter(URL.short_id == short_id).first()
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=db_url.original_url)
