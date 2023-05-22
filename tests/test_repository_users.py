from datetime import datetime
from fastapi import HTTPException
import unittest
from unittest.mock import MagicMock

from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.database.models import Role, User
from src.repository.users import (
                                  get_user_by_email,
                                  get_user_by_id,
                                  create_user,
                                  change_password_for_user,
                                  update_token,
                                  confirmed_email,
                                  update_avatar,
                                  get_number_of_images_per_user,
                                  update_user_profile,
                                  update_your_profile,
                                  ban_user,
                                  )
from src.schemas.users import UserBase, UserModel, UserType

class TestUsers(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        """Start before all test."""
        cls.password = 'new_passw0rd'
        cls.email = 'Unknown2@mail.com'
        cls.user_id = 3
        cls.role = UserType(
                            username='NewName',
                            email=EmailStr('Unknown3@mail.com'),
                            roles='moderator'
                            )
        cls.body_base = UserBase(
                                 username='NewName', 
                                 email=EmailStr('NewEMail@mail.com')
                                 )
        cls.body_user_model = UserModel(
                                        username='Unknown2', 
                                        email=EmailStr('Unknown2@mail.com'),
                                        password='Qwerty@123',
                                        )
        cls.admin = User(
                         id=1, 
                         username='Admin', 
                         email=EmailStr('Unknown1@mail.com'),
                         password='Qwerty@123',
                         created_at=datetime.now(),
                         updated_at=datetime.now(),
                         avatar='default',
                         refresh_token='eyJhb...-iV1MI',
                         roles=Role.admin,
                         confirmed=True,
                         status_active=True
                         )
        cls.user = User(
                        id=2, 
                        username='User', 
                        email=EmailStr('Unknown2@mail.com'),
                        password='Qwerty@123',
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        avatar='non-standard',
                        refresh_token='ey.....37Ns5pX-iV1MI',
                        roles=Role.user,
                        confirmed=False,
                        status_active=True
                        )

    # @classmethod
    # def tearDownClass(cls):
    #     """Start after all test."""
    #     ...

    def setUp(self):
        """Start before each test."""
        self.session = MagicMock(spec=Session)

    # def tearDown(self):
    #     """Start after each test."""
    #     ...

    async def test_get_user_by_email_found(self):
        self.session.query().filter().first.return_value = TestUsers.user
        result = await get_user_by_email(email=self.user.email, db=self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result, TestUsers.user)
        [self.assertEqual(result.__dict__[el], TestUsers.user.__dict__[el])
            for el in TestUsers.user.__dict__]

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email=self.email, db=self.session)  # self.email === TestUsers.email
        self.assertIsNone(result)
    
    async def test_get_user_by_id_found(self):
        self.session.query().filter().first.return_value = TestUsers.user
        result = await get_user_by_id(user_id=self.user.id, db=self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result, TestUsers.user)
        [self.assertEqual(result.__dict__[el], TestUsers.user.__dict__[el])
            for el in TestUsers.user.__dict__]
    
    async def test_get_user_by_id_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_id(user_id=self.user_id, db=self.session)
        self.assertIsNone(result)

    async def test_create_user_first_success(self):  # admin
        self.session.query().first.return_value = None
        result: User = await create_user(body=TestUsers.body_user_model, db=self.session)
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.admin.__dict__]
        [self.assertEqual(result.__dict__[el], TestUsers.body_user_model.__dict__[el]) for el in TestUsers.body_user_model.__dict__]
        self.assertEqual(result.roles, TestUsers.admin.roles)
    
    async def test_create_user_success(self):  # user
        self.session.query().first.return_value = TestUsers.admin
        result: User = await create_user(body=TestUsers.body_user_model, db=self.session)
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.admin.__dict__]
        [self.assertEqual(result.__dict__[el], TestUsers.body_user_model.__dict__[el]) for el in TestUsers.body_user_model.__dict__]
        self.assertEqual(result.roles, TestUsers.user.roles)
    
    async def test_create_user_fail(self):  # in auth-rout when signUp
        return

    async def test_change_password_for_user(self):
        result: User = await change_password_for_user(user=TestUsers.user, password=self.password, db=self.session)
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.user.__dict__]
        self.assertEqual(result.password, self.password)
    
    async def test_update_token(self):
        result: User = await update_token(user=TestUsers.user, token=self.admin.refresh_token, db=self.session)
        self.assertEqual(self.user.refresh_token, self.admin.refresh_token)
        self.assertIsNone(result)
        
    async def test_confirmed_email(self):
        self.assertEqual(self.user.confirmed, False)
        result: User = await confirmed_email(user=TestUsers.user, db=self.session)
        self.assertEqual(self.user.confirmed, True)
        self.assertIsNone(result)

    async def test_update_avatar_success(self):
        self.session.query().filter().first.return_value = TestUsers.admin
        result: User = await update_avatar(email=TestUsers.admin.email, url=TestUsers.user.avatar, db=self.session)
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.admin.__dict__]
        self.assertEqual(TestUsers.admin.avatar, TestUsers.user.avatar)
    
    async def test_update_avatar_fail(self):
        self.session.query().filter().first.return_value = None
        result = await update_avatar(email=self.email, url=TestUsers.user.avatar, db=self.session)
        self.assertIsNone(result)
    
    async def test_get_number_of_images_per_user(self):
        self.session.query().filter().count.return_value = 0
        result: User = await get_number_of_images_per_user(email=TestUsers.admin.email, db=self.session)
        self.assertEqual(result, 0)
        self.session.query().filter().count.return_value = 17
        result: User = await get_number_of_images_per_user(email=TestUsers.admin.email, db=self.session)
        self.assertEqual(result, 17)
    
    async def test_update_user_profile_success(self):
        self.session.query().filter().first.return_value = TestUsers.user
        result: User = await update_user_profile(
                                                 user_id=TestUsers.user.id, 
                                                 current_user=TestUsers.admin.__dict__,
                                                 body_data=self.role,
                                                 db=self.session
                                                 )
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.user.__dict__]
        self.assertEqual(result.roles, TestUsers.user.roles)
        self.assertEqual(self.role.roles, TestUsers.user.roles.value)
    
    async def test_update_user_profile_fails(self):
        self.session.query().filter().first.return_value = None
        result: None = await update_user_profile(
                                                 user_id=TestUsers.user.id, 
                                                 current_user=TestUsers.admin.__dict__,
                                                 body_data=self.role,
                                                 db=self.session
                                                 )
        self.assertIsNone(result)

        self.session.query().filter().first.return_value = TestUsers.user
        result: User = await update_user_profile(
                                                 user_id=TestUsers.user.id, 
                                                 current_user=TestUsers.admin.__dict__,
                                                 body_data=None,
                                                 db=self.session
                                                 )
        self.assertIsNone(result)

        self.session.query().filter().first.return_value = TestUsers.user
        result: User = await update_user_profile(
                                                 user_id=TestUsers.user.id, 
                                                 current_user=TestUsers.user.__dict__,
                                                 body_data=self.role,
                                                 db=self.session
                                                 )
        self.assertIsNone(result)

        self.session.query().filter().first.return_value = TestUsers.admin
        result: User = await update_user_profile(
                                                 user_id=TestUsers.admin.id, 
                                                 current_user=TestUsers.admin.__dict__,
                                                 body_data=self.role,
                                                 db=self.session
                                                 )
        self.assertIsNone(result)

    async def test_update_your_profile_success(self):
        self.session.query().filter().first.return_value = TestUsers.admin
        result: User = await update_your_profile(
                                                 email=TestUsers.admin.email, 
                                                 body_data=self.body_base, 
                                                 db=self.session
                                                 )
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.admin.__dict__]
        [self.assertEqual(result.__dict__[el], self.body_base.__dict__[el]) for el in self.body_base.__dict__]
    
    async def test_update_your_profile_fail(self):
        self.session.query().filter().first.return_value = None
        result = await update_your_profile(email=TestUsers.admin.email, body_data=self.body_base, db=self.session)
        self.assertIsNone(result)
        self.session.query().filter().first.return_value = TestUsers.admin
        result = await update_your_profile(email=TestUsers.admin.email, body_data=None, db=self.session)
        self.assertIsNone(result)
    
    async def test_ban_user_success(self):
        self.assertEqual(self.user.status_active, True)
        self.session.query().filter_by().first.return_value = TestUsers.user
        result: User = await ban_user(user_id=TestUsers.user.id, active_status=False, db=self.session)
        [self.assertTrue(hasattr(result, el)) for el in TestUsers.user.__dict__]
        self.assertEqual(result.status_active, False)
        self.assertEqual(self.user.status_active, False)

    async def test_ban_user_fail(self):
        self.session.query().filter_by().first.return_value = None
        result = await ban_user(user_id=TestUsers.user_id, active_status=False, db=self.session)
        self.assertIsNone(result)
        self.session.query().filter_by().first.return_value = TestUsers.admin
        with self.assertRaises(HTTPException) as context:
            await ban_user(user_id=TestUsers.admin.id, active_status=False, db=self.session)
        self.assertTrue(context.exception)

if __name__ == '__main__':
    unittest.main()
