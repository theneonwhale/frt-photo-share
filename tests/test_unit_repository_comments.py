import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.conf import messages
from src.database.models import Comment, Image
from src.schemas.images import CommentModel

from src.repository.comments import (
    add_comment,
    update_comment,
    remove_comment,
    get_comments

)


class TestComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.image = Image(id=1)
        self.user = {'id': 1, 'roles': 'user'}

    async def test_get_comments(self):
        comments = [Comment(), Comment()]
        self.session.query.return_value.filter_by.return_value.all.return_value = comments
        result = await get_comments(image_id=self.image.id, db=self.session)
        self.assertEqual(result, comments)
        self.session.query.assert_called_once_with(Comment)
        self.session.query.return_value.filter_by.assert_called_once_with(image_id=self.image.id)
        self.session.query.return_value.filter_by.return_value.all.assert_called_once()

    async def test_add_comment(self):
        comment = CommentModel(comment='Test comment')

        result = await add_comment(body=comment, image_id=1, user=self.user, db=self.session)

        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.comment, comment.comment)
        self.assertEqual(result.user_id, self.user['id'])

    async def test_remove_contact(self):
        comment = Comment()
        self.session.query.return_value.filter_by.return_value.first.return_value = comment
        result = await remove_comment(comment_id=comment.id, user=self.user, db=self.session)
        self.assertEqual(result['message'], messages.COMMENT_DELETED)
        self.session.query.assert_called_once_with(Comment)
        self.session.query.return_value.filter_by.assert_called_once_with(id=comment.id)
        self.session.delete.assert_called_once_with(comment)
        self.session.commit.assert_called_once()



    async def test_update_comment(self):
        comment_id = 1
        body = CommentModel(comment='Updated comment')
        expected_comment = Comment(comment=body.comment, user_id=self.user['id'], image_id=None)

        self.session.query.return_value.filter_by.return_value.first.return_value = expected_comment
        self.session.commit.return_value = None
        self.session.refresh.return_value = None

        comment = await update_comment(comment_id, body, self.user, self.session)

        self.assertEqual(comment, expected_comment)
        self.session.query.assert_called_once_with(Comment)
        self.session.query.return_value.filter_by.assert_called_once_with(id=comment_id, user_id=self.user['id'])
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(expected_comment)


if __name__ == '__main__':
    unittest.main()
