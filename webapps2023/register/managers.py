from django.contrib.auth.models import Group
from django.contrib.auth.base_user import BaseUserManager
from .management.user_groups import UserGroups
from django.shortcuts import get_object_or_404


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier, but emails have to be unique as well
    """
    use_in_migrations = True

    def create_user(self, email, username, first_name, last_name, password, currency="", **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        is_administrator = extra_fields.get("is_superuser") is True or extra_fields.get("is_admin") is True

        # All Users validation
        if not email:
            raise ValueError("The Email must be set")
        if not username:
            raise ValueError("The Username must be set")
        if not first_name:
            raise ValueError("The First Name must be set")
        if not last_name:
            raise ValueError("The Last Name must be set")

        # Regular/Public User validation
        if not is_administrator:
            if not currency:
                raise ValueError("The Currency must be set")

        # Admin/Super User validation
        if is_administrator:
            if password is None:
                password = self.make_random_password()
            if not extra_fields.get("is_active"):
                extra_fields.setdefault("is_active", True)

        # All Users account creation
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            currency=currency,
            **extra_fields
        )
        user.set_password(password)
        user.save()

        # Add user to a permission group
        if not is_administrator:
            customers_group, created = Group.objects.get_or_create(name=UserGroups.CUSTOMERS.value)

            if created:
                print("Created customers group")

            # Regular/Customer users
            user.groups.add(customers_group)
        elif extra_fields.get("is_admin") and not extra_fields.get("is_superuser"):
            # superusers have all permissions by default
            # Non-superuser admins
            admins_group, created = Group.objects.get_or_create(name=UserGroups.ADMINS.value)

            if created:
                print("Created admins group")

            user.groups.add(admins_group)

        # Reload the user to avoid permission cache problem in testing
        user = get_object_or_404(self.model, username=username)

        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_admin") is not True:
            raise ValueError("Superuser must have is_admin=True.")
        return self.create_user(email, username, first_name, last_name, password, **extra_fields)