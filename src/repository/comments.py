from typing import Optional, List

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from src.database.models import Comment, User
from src.schemas.images import CommentModel
from src.conf import messages


async def add_comment(
        body: CommentModel,
        image_id: int,
        user: dict,
        db: Session
        ) -> Optional[Comment]:
    """
    The add_comment function creates a new comment for an image.
    Args:
    body (CommentModel): The CommentModel object containing the comment to be added.
    image_id (int): The id of the image that is being commented on.
    user (dict): A dictionary containing information about the user who is adding a comment, including their id and username.

    :param body: CommentModel: Get the comment from the request body
    :param image_id: int: Get the image id from the url
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
        ) -> Optional[Comment]:
    """
    The update_comment function updates a comment in the database.
    Args:
    comment_id (int): The id of the comment to update.
    body (CommentModel): The updated Comment object with new values for its attributes.
    This is passed as JSON from the client and converted into a CommentModel object by Pydantic's BaseModel class.
    See models/comment_model for more information on how this works, or visit https://pydantic-docs.helpmanual.io/.

    :param comment_id: int: Identify the comment to be deleted
    :param body: CommentModel: Get the comment from the request body
    :param user: dict: Check if the user is authorized to delete a comment
    :param db: Session: Access the database
    :param : Get the comment id
    :return: The updated comment
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
    ) -> dict:
    """
    The remove_comment function deletes a comment from the database.

    :param comment_id: int: Specify the id of the comment that is to be deleted
    :param user: User: Check if the user is authorized to delete a comment
    :param db: Session: Access the database
    :return: A dictionary with a message that the comment has been deleted
    :doc-author: Trelent
    """
    comment: Comment = db.query(Comment).filter_by(id=comment_id).first()

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.MSC404_COMMENT_NOT_FOUND)

    db.delete(comment)
    db.commit()

    return {'message': messages.COMMENT_DELETED}


async def get_comments(image_id, db) -> List[Comment]:
    """
    The get_comments function takes in an image_id and a database connection,
    and returns all comments associated with the given image_id.

    :param image_id: Filter the comments by image_id
    :param db: Query the database for comments that are associated with a specific image
    :return: All comments associated with a particular image
    :doc-author: Trelent
    """
    return db.query(Comment).filter_by(image_id=image_id).all()
