from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models import Artwork
from models.user import User, UserRole
from schemas import ArtworkCreate, ArtworkResponse
from utils.auth import get_current_user, require_seller

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
async def create_artwork(
    artwork: ArtworkCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Create a new artwork.

    SECURITY: seller_id is extracted from the authenticated user's JWT token.
    Only users with SELLER or ADMIN role can create artworks.
    This prevents artwork creation with forged seller_id.
    """
    # Create artwork with authenticated user's ID
    db_artwork = Artwork(**artwork.dict(), seller_id=current_user.id)
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork


@router.get("/my-artworks", response_model=List[ArtworkResponse])
async def get_my_artworks(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db),
):
    """
    Get all artworks owned by the authenticated seller.

    SECURITY: Only returns artworks where seller_id matches the authenticated user.
    Requires SELLER or ADMIN role.
    """
    artworks = db.query(Artwork).filter(Artwork.seller_id == current_user.id).all()
    return artworks


@router.post("/{artwork_id}/upload-image")
async def upload_artwork_image(
    artwork_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    return {"message": "Image upload endpoint - to be implemented"}
