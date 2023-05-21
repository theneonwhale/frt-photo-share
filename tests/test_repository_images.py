import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import Image, Tag
from src.schemas.images import ImageModel

from src.repository.images import (
    create_image,
    get_image,
    get_images,
    transform_image,
    remove_image,
    update_image,
    get_images_by_tag,
    get_images_by_user
)

'''
Unit tests for the application.
'''

'''
Test src.repository.images 
1. create_image,
2. get_image,
3. get_images,
4. transform_image,
5. remove_image,
6. update_image,
7. get_images_by_tag,
8. get_images_by_user
'''


class TestImagesRepository(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = {'id': 1, 'roles': 'user'}

    async def test_create_image(self):
        image = ImageModel(name='Test image', description='Test description', tags=['test', 'image'])
        result = await create_image(body=image, user=self.user, db=self.session)
        self.assertTrue(hasattr(result, 'id'))
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.user_id, self.user['id'])
        self.assertEqual(result.tags, image.tags)

    async def test_get_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await get_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)

    async def test_get_images(self):
        images = [Image(), Image()]
        self.session.query().filter_by().offset().limit().all.return_value = images
        result = await get_images(user=self.user, db=self.session)
        self.assertEqual(result, images)

    async def test_transform_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await transform_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)

    async def test_remove_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await remove_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)

    async def test_update_image(self):
        image = Image()
        self.session.query().filter_by().first.return_value = image
        result = await update_image(image_id=image.id, user=self.user, db=self.session)
        self.assertEqual(image, result)

    async def test_get_images_by_tag(self):
        images = [Image(), Image()]
        self.session.query().filter_by().offset().limit().all.return_value = images
        result = await get_images_by_tag(tag='test', user=self.user, db=self.session)
        self.assertEqual(result, images)

    async def test_get_images_by_user(self):
        images = [Image(), Image()]
        self.session.query().filter_by().offset().limit().all.return_value = images
        result = await get_images_by_user(user_id=self.user['id'], user=self.user, db=self.session)
        self.assertEqual(result, images)


if __name__ == '__main__':
    unittest.main()
