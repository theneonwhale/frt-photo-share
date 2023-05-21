from typing import List

from sqlalchemy.orm import Session

from src.database.models import Tag


async def create_tag(name, db: Session) -> Tag:
    tag = Tag(name=name)

    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag


async def get_tags(db: Session) -> List[Tag]:
    return db.query(Tag).all()


async def get_tag(tag_id: int, db: Session) -> Tag:
    return db.query(Tag).filter(Tag.id == tag_id).first()


async def get_tag_by_name(name: str, db: Session) -> Tag:
    return db.query(Tag).filter_by(name=name).first()
