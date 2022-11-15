"""Test for admin modifications"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """test for admin """

    def setUp(self):
        """test on creating user and client"""
        self.client = Client()
        self.admin_user = get_user_model().objects. \
            create_superuser(  # type: ignore
            email='admin.s@example.com',
            password='passtest12345'
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(  # type: ignore
            email='user@example.com',
            password="testpass123",
            name="New User"
        )

    def test_user_list(self):
        """Test if user are listed or not"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test if the custom admin user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
