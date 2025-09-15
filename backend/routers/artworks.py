from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Artwork, User
from schemas import ArtworkCreate, ArtworkResponse

router = APIRouter()

@router.get("/", response_model=List[ArtworkResponse])
async def get_artworks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    artworks = db.query(Artwork).offset(skip).limit(limit).all()
    return artworks

@router.get("/{artwork_id}", response_model=ArtworkResponse)
async def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork

@router.post("/", response_model=ArtworkResponse)
async def create_artwork(artwork: ArtworkCreate, db: Session = Depends(get_db)):
    db_artwork = Artwork(**artwork.dict())
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork

@router.post("/{artwork_id}/upload-image")
async def upload_artwork_image(artwork_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # TODO: Implement image upload logic with aiofiles and Pillow
    return {"message": "Image upload endpoint - to be implemented"}