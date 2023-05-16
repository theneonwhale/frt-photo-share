from typing import Optional

from fastapi.encoders import jsonable_encoder
from libgravatar import Gravatar  # poetry add libgravatar
from sqlalchemy.orm import Session

from src.database.models import Image, Role, User
from src.schemas import UserModel, UserType
from src.services.auth import authpassword


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


async def get_user_by_id(id: int, db: Session) -> User:
    return db.query(User).filter(User.id == id).first()


async def create_user(body: UserModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)  # object creates based on e-mail
        avatar = g.get_image()  # holds the avatar URL from the Gravatar API

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
    # user: User = await get_user_by_id(user.id, db)
    user.password = password
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def update_token(user: User, token: str | None, db: Session) -> None:
    # user: User = await get_user_by_id(user.id, db)
    user.refresh_token = token
    db.commit()


async def confirmed_email(user: User, db: Session) -> None:
    # user: User = await get_user_by_email(user.email, db)
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


async def update_user(email: str, body_data: UserType, db: Session) -> Optional[User]:
    user: User = await get_user_by_email(email, db)
    if not user:
        return None

    db_obj_data: Optional[dict] = user.__dict__  # if user else None
    body_data: Optional[dict] = jsonable_encoder(body_data) if body_data else None
    
    if not db_obj_data or not body_data:
        return None

    if user.roles != Role.admin:
        body_data.pop('roles')

    else:
        body_data['roles'] = Role.admin if body_data['roles'].lower() == 'admin' else Role.moderator if body_data['roles'].lower() == 'moderator' else Role.user

    if body_data['password']:
        body_data['password'] =  authpassword.get_hash_password(body_data['password'])

    for field in db_obj_data:
        if field in body_data:
            setattr(user, field, body_data[field])  # username, email, password ...  ! + avatar[to fix UserModel?] or separately?

    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
