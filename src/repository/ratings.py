from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.conf import messages
from src.database.models import Rating, Image, User
from src.schemas.images import RatingModel


async def add_rating(
                     body: RatingModel,
                     image_id: int,
                     user: dict,
                     db: Session
                     ) -> Rating:
    rating = Rating(
                    rating=body.rating,
                    user_id=user['id'],
                    image_id=image_id
                    )
    db.add(rating)
    db.commit()
    db.refresh(rating)

    image = db.query(Image).get(image_id)
    average_rating = db.query(func.avg(Rating.rating)).filter(Rating.image_id == image_id).scalar()
    image.rating = average_rating

    db.commit()
    db.refresh(image)

    return rating


async def get_ratings(
                image_id: int,
                db: Session
                ) -> List[Rating]:
    ratings = db.query(Rating).filter(Rating.image_id == image_id).all()

    return ratings


async def remove_rating(
                         rating_id: int,
                         user: User,
                         db: Session
                         ) -> dict:
    rating = db.query(Rating).filter_by(id=rating_id).first()

    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_RATING_NOT_FOUND)

    image_id = rating.image_id

    db.delete(rating)
    db.commit()

    image = db.query(Image).get(image_id)
    average_rating = db.query(func.avg(Rating.rating)).filter(Rating.image_id == image_id).scalar()
    image.rating = average_rating

    db.commit()
    db.refresh(image)

    return {'message': messages.RATING_DELETED}
