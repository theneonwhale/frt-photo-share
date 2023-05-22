import asyncio
from datetime import date
import unittest
from unittest.mock import MagicMock
from fastapi import HTTPException

from fastapi_pagination import Page, Params
from pydantic import EmailStr
from sqlalchemy.orm import Session


async def async_add(a, b):
    await asyncio.sleep(1)
    return a + b


class TestUsers(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        """Start before all test."""
        cls.name = 'New_Name'
        cls.email = 'Unknown2@mail.com'
        cls.user = User(id=1)

    @classmethod
    def tearDownClass(cls):
        """Start after all test."""
        ...

    def setUp(self):
        """Start before each test."""
        """
         створюємо об'єкт MagicMock для заміни об'єкта Session у модульних тестах MagicMock(spec=Session).
         У цьому випадку, MagicMock використовується для створення "фіктивного" об'єкта Session, 
         а використання параметра spec=Session у конструкторі MagicMock вказує, що створюваний об'єкт 
         матиме ті самі атрибути і методи, що й об'єкт Session
        """
        self.session = MagicMock(spec=Session)
        # self.user = User(id=1)

    def tearDown(self):
        """Start after each test."""
        ...



    #...
    async def test_add(self):
        """Add function test."""
        r = await async_add(2, 3)
        self.assertEqual(r, 5)


if __name__ == '__main__':
    unittest.main()