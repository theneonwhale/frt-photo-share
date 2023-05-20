from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import Comment, Image, User
from src.schemas.images import CommentModel


async def add_comment(
        body: CommentModel,
        image_id: int,
        user: dict,
        db: Session
        ) -> Optional[Comment]:
    """
    The add_comment function creates a new comment for an image.

    :param body: CommentModel: Get the comment from the request body
    :param image_id: int: Get the image id from the database
    :param user: dict: Get the user id from the token
    :param db: Session: Access the database
    :return: A comment object
    :doc-author: Trelent
    """
    comment = Comment(
        comment=body.comment,
        user_id=user['id'],
        image_id=image_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


async def update_comment(
                         comment_id: int,
                         body: CommentModel,
                         user: dict,
                         db: Session,
                         ) -> Optional[Image]:

    """
    The update_comment function updates a comment in the database.
    Args:
    comment_id (int): The id of the comment to update.
    body (CommentModel): The updated Comment object to be stored in the database.
    This is passed as JSON from the client and converted into a CommentModel object by Pydantic's BaseModel class.
    See models/comment for more information on how this works, or visit https://pydantic-docs.helpmanual.io/.

    :param comment_id: int: Identify the comment to be deleted
    :param body: CommentModel: Get the comment from the request body
    :param user: dict: Get the user id from the jwt token
    :param db: Session: Access the database
    :param : Determine which comment to delete
    :return: A comment object
    :doc-author: Trelent
    """
    comment: Comment = db.query(Comment).filter_by(id=comment_id, user_id=user['id']).first()
    if not comment or not body.comment:
        return None

    comment.comment = body.comment
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


async def remove_comment(
                         comment_id: int,
                         user: User,
                         db: Session
                         ) -> Optional[Image]:

    """
    The remove_comment function removes a comment from the database.
    Args:
    comment_id (int): The id of the comment to be removed.
    user (User): The user who is removing the image.  This is used for authorization purposes only, and not stored in any way by this function or its helpers.

    :param comment_id: int: Find the comment in the database
    :param user: User: Check if the user is logged in
    :param db: Session: Access the database
    :return: A comment object
    :doc-author: Trelent
    """
    comment: Comment = db.query(Comment).filter_by(id=comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()

    return comment


async def get_comments(image_id, db):

    """
    The get_comments function takes in an image_id and a database connection object.
    It then queries the Comment table for all comments with the given image_id, and returns them as a list.

    :param image_id: Filter the comments by image_id
    :param db: Access the database
    :return: All comments for a given image
    :doc-author: Trelent
    """
    return db.query(Comment).filter_by(image_id=image_id).all()
