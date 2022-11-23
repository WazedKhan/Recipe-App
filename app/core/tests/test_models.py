"""
Contains all the test cases for models of core app
"""
from unittest.mock import patch
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


def create_user(email='user@example.com', password='user123pass'):
    """Helper function for creating user for test case"""
    return get_user_model().objects.create_user(email, password)  # type: ignore # noqa


class ModelTests(TestCase):
    """Test models class"""

    def test_create_user_with_email_successful(self):
        """run a test to create a user with email"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(  # type:ignore
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test email is normailzed for new user"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(  # type:ignore
                email, 'sample123'
                )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Tast that if a user is creating without a email
            raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')  # type:ignore

    def test_create_superuser(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(  # type:ignore
            'test123@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_creating_recipe(self):
        """Test creating recipe model is success"""
        user = get_user_model().objects.create_user(  # type:ignore
            'test@example.com',
            'pass123test'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample Recipe Name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample Recipe Description'
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='tag1')

        self.assertEqual(str(tag), tag.name)  # type: ignore

    def test_create_ingredient(self):
        """Test creating a ingredient model is successful"""
        ingredient = models.Ingredient.objects.create(
            user=create_user(),
            name='ingredient1'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
