import os
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.orm import Session

from database import get_db
from models import Artwork
from models.user import User, UserRole
from schemas import ArtworkCreate, ArtworkResponse, ArtworkUpdate
from services.auction_service import AuctionService
from utils.auth import get_current_user, require_admin, require_seller

router = APIRouter()


@router.get("/", response_model=List[ArtworkResponse])
async def get_artworks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get list of artworks with pagination.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)
    """
    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip parameter must be non-negative"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit parameter must be at least 1"
        )

    # Enforce maximum limit to prevent resource exhaustion
    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit cannot exceed 100"
        )

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
    # Validate secret_threshold
    if artwork.secret_threshold < 0:
        raise HTTPException(
            status_code=400,
            detail="Secret threshold must be non-negative"
        )

    # Validate title length
    if len(artwork.title) < 3:
        raise HTTPException(
            status_code=400,
            detail="Title must be at least 3 characters long"
        )
    if len(artwork.title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Title cannot exceed 200 characters"
        )

    # Validate description length if provided
    if artwork.description and len(artwork.description) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Description cannot exceed 2000 characters"
        )

    # Validate end_date is in future if provided
    if artwork.end_date and artwork.end_date < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="End date must be in the future"
        )

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


@router.put("/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: int,
    artwork_update: ArtworkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update artwork details (only owner or admin).

    SECURITY: Only the artwork owner or admin can update artwork details.
    Sellers cannot update other sellers' artworks.
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check ownership
    if artwork.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this artwork"
        )

    # Validate updated fields
    update_data = artwork_update.dict(exclude_unset=True)

    if "secret_threshold" in update_data and update_data["secret_threshold"] < 0:
        raise HTTPException(
            status_code=400,
            detail="Secret threshold must be non-negative"
        )

    if "title" in update_data:
        if len(update_data["title"]) < 3:
            raise HTTPException(
                status_code=400,
                detail="Title must be at least 3 characters long"
            )
        if len(update_data["title"]) > 200:
            raise HTTPException(
                status_code=400,
                detail="Title cannot exceed 200 characters"
            )

    if "description" in update_data and update_data["description"] and len(update_data["description"]) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Description cannot exceed 2000 characters"
        )

    if "end_date" in update_data and update_data["end_date"] and update_data["end_date"] < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="End date must be in the future"
        )

    # Update fields
    for field, value in update_data.items():
        setattr(artwork, field, value)

    db.commit()
    db.refresh(artwork)
    return artwork


@router.delete("/{artwork_id}")
async def delete_artwork(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete artwork (only owner or admin).

    SECURITY: Only the artwork owner or admin can delete artwork.
    Cannot delete sold artworks to maintain transaction history.
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check ownership
    if artwork.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this artwork"
        )

    # Check if artwork is sold
    if artwork.status == "SOLD":
        raise HTTPException(
            status_code=400, detail="Cannot delete sold artwork"
        )

    db.delete(artwork)
    db.commit()
    return {"message": "Artwork deleted successfully"}


@router.post("/{artwork_id}/upload-image")
async def upload_artwork_image(
    artwork_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload artwork image (only owner or admin).

    SECURITY: Only the artwork owner or admin can upload images.
    Validates file type and size to prevent abuse.
    """
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check ownership
    if artwork.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Not authorized to upload image for this artwork"
        )

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
        )

    # Read file contents
    contents = await file.read()

    # Validate file size (max 5MB)
    MAX_SIZE = 5 * 1024 * 1024
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Save to uploads directory
    upload_dir = "uploads/artworks"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)

    # Optional: Resize/optimize image with Pillow
    try:
        img = Image.open(file_path)
        # Resize if too large (max 1200px on longest side)
        img.thumbnail((1200, 1200))
        img.save(file_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Image optimization failed: {e}")
        # Continue anyway - image is saved but not optimized

    # Update artwork with image URL
    artwork.image_url = f"/uploads/artworks/{unique_filename}"
    db.commit()

    return {"message": "Image uploaded successfully", "image_url": artwork.image_url}


@router.post("/expire-auctions")
async def expire_auctions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Manually trigger auction expiration check (admin only).

    SECURITY: Only admins can trigger this endpoint.
    Closes all auctions past their end_date.
    """
    count = AuctionService.check_expired_auctions(db)
    return {"message": f"Closed {count} expired auctions"}
