"""
Test Tag models API's
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from recipe.serializers import TagSerializer
from core.models import Tag


TAGS_URL = reverse('recipe:tag-list')


def create_user(email='user@example.com', password='user123pass'):
    """Create and return a user for helping test cases"""
    return get_user_model().objects.create_user(email=email, password=password)  # type: ignore # noqa


class PublicTagsApiTest(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test on retrieving data user need to be authenticated"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test on retriveing list of tags"""
        Tag.objects.create(user=self.user, name='Non-Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # type: ignore
        self.assertEqual(res.data[0]['name'], tag.name)  # type: ignore
        self.assertEqual(res.data[0]['id'], tag.id)  # type: ignore
