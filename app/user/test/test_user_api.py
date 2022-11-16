"""
Tests for user api's
"""
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """create and returns new user"""
    return get_user_model().objects.create_user(**params)  # type:ignore


class PublicUserApiTests(TestCase):
    '''Test the public features for the user api'''
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Tests if user create is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Testing Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(  # type:ignore \
            payload['password']))
        self.assertNotIn('password', res.data)  # type:ignore

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Testing Name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less then 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Testing Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test create token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }
        create_user(**user_details)
        paylaod = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, paylaod)

        self.assertIn('token', res.data)  # type:ignore
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        create_user(email='test@example.com', password='testpass')
        paylaod = {'email': 'test@example.com', 'password': 'badpass'}

        res = self.client.post(TOKEN_URL, paylaod)
        self.assertNotIn('token', res.data)  # type:ignore
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)  # type:ignore
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)