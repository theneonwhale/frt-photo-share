from typing import Optional

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import Image, Role, User

from src.schemas.users import UserBase, UserModel, UserType
from src.conf import messages


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def get_user_by_id(user_id: int, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()


async def create_user(body: UserModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()

    except Exception as e:
        print(e)

    new_user: User = User(**body.dict(), avatar=avatar)
    if not db.query(User).first():
        new_user.roles = Role.admin

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def change_password_for_user(user: User, password: str, db: Session) -> User:
    user.password = password
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def confirmed_email(user: User, db: Session) -> None:
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> Optional[User]:
    user: User = await get_user_by_email(email, db)
    if user:
        user.avatar = url
        db.commit()
        db.refresh(user)

        return user


async def get_number_of_images_per_user(email: str, db: Session) -> int:
    return db.query(Image).filter(User.email == email).count()


async def update_user_profile(user_id: int, current_user: dict, body_data: UserType, db: Session) -> Optional[User]:
    user: User = await get_user_by_id(user_id, db)
    if not user:
        return None
    
    db_obj_data: Optional[dict] = user.__dict__
    body_data: Optional[dict] = jsonable_encoder(body_data) if body_data else None
    if (
        user_id == current_user['id'] and 
        body_data['roles'] != 'admin' and 
        not db.query(User).filter(User.roles == Role.admin)
        ):
        body_data.pop('roles')

    else:
        role_mapping = {
                        'admin': Role.admin,
                        'moderator': Role.moderator,
                        'user': Role.user
                        }
        body_data['roles'] = role_mapping.get(body_data['roles'].lower(), Role.user)

    for field in db_obj_data:
        if field in body_data:
            setattr(user, field, body_data[field])
            
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def update_your_profile(email: str, body_data: UserBase, db: Session) -> Optional[User]:
    user: User = await get_user_by_email(email, db)
    if not user:
        return None
    
    db_obj_data: Optional[dict] = user.__dict__
    body_data: Optional[dict] = jsonable_encoder(body_data) if body_data else None
    if not db_obj_data or not body_data:
        return None
    
    for field in db_obj_data:
        if field in body_data:
            setattr(user, field, body_data[field])

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def ban_user(user_id, active_status, db):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return None
    
    if user.roles.value == 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.MSC403_USER_BANNED)
    
    user.status_active = active_status
    db.commit()
    db.refresh(user)

    return user
