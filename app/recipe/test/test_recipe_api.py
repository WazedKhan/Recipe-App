"""Test for recipe APIs"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """create and returns a sample recipe"""
    defaults = {
        'title': 'Sample Recipe Title',
        'time_minutes': 22,
        'price': Decimal('5.22'),
        'description': 'Sample Description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)  # type: ignore


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call the API"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test authenticated API call"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com', password='passw123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieving list of recipe"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type:ignore

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""
        other_user = create_user(email='user@example.com', password='test123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type:ignore

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)  # type:ignore
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)  # type:ignore

    def test_create_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'Sample Recipe',
            'description': 'Sample Description',
            'time_minutes': 30,
            'price': Decimal('50.30')
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])  # type:ignore
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update on recipe"""
        original_link = 'http://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            description='sample description',
            title='sample title',
            link=original_link
        )

        paylod = {'title': 'new title recipe'}
        url = detail_url(recipe.id)  # type: ignore
        res = self.client.patch(url, paylod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, paylod['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def text_full_update_recipe(self):
        """Test full update of recipe"""
        recipe = create_recipe(
            user=self.user,
            title='sample title',
            description='sample description',
            link='http://example.com/recipe.pdf'
        )

        payload = {
            'title': 'New Recipe Title',
            'link': 'http://example.com/new/recipe.pdf',
            'description': 'New Recipe Description',
            'time_minutes': 10,
            'price': Decimal('6.30')
        }
        url = detail_url(recipe.id)  # type: ignore
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user result in an error"""
        new_user = create_user(
            email='newuser@example.com', password='newuser123'
            )
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)  # type: ignore
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def text_delete_recipe(self):
        """Test deleting recipe"""
        recipe = create_recipe(
            user=self.user
        )
        url = detail_url(recipe.id)  # type:ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id))  # type: ignore

    def test_recipe_other_user_recipe_error(self):
        """Test trying to delete other user recipe gives error"""

        new_user = create_user(
            email='newuser@example.com',
            password='newpass123'
        )
        recipe = create_recipe(
            user=new_user
        )

        url = detail_url(recipe.id)  # type: ignore
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id))  # type:ignore
