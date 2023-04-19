from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Currency


class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", username="normal", first_name="John", last_name="Doe", currency=Currency.GBP, password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertEqual(user.username, "normal")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_admin)

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="", username="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", username="", first_name="", last_name="", password="foo")

    def test_create_admin(self):
        User = get_user_model()
        admin_user = User.objects.create_user(email="admin@user.com", username="admin1", first_name="John", last_name="Doe", password="foo", is_admin=True)
        self.assertEqual(admin_user.email, "admin@user.com")
        self.assertEqual(admin_user.username, "admin1")
        self.assertEqual(admin_user.first_name, "John")
        self.assertEqual(admin_user.last_name, "Doe")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_staff)


    def test_create_superuser(self):
        User = get_user_model()
        super_user = User.objects.create_superuser(email="super@user.com", username="super1", first_name="John", last_name="Doe", password="foo")
        self.assertEqual(super_user.email, "super@user.com")
        self.assertEqual(super_user.username, "super1")
        self.assertEqual(super_user.first_name, "John")
        self.assertEqual(super_user.last_name, "Doe")
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_superuser)

        with self.assertRaises(TypeError):
            User.objects.create_superuser(
                email="super@user.com", username="super1", password="foo", is_superuser=True)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", username="super1", first_name="John", last_name="Doe", password="foo", is_superuser=False)
