from django.contrib.auth.models import Group
from django.contrib.auth.base_user import BaseUserManager
from .management.user_groups import UserGroups
from django.shortcuts import get_object_or_404


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier, but emails have to be unique as well
    """
    use_in_migrations = True

    @staticmethod
    def assign_permission_groups(user):

        # Add user to a permission group
        if not user.is_admin:
            customers_group, created = Group.objects.get_or_create(name=UserGroups.CUSTOMERS)

            if created:
                print(f'Created {UserGroups.CUSTOMERS} group')

            # Regular/Customer users
            user.groups.add(customers_group)
        elif user.is_admin and not user.is_superuser:
            # superusers have all permissions by default
            # Non-superuser admins
            admins_group, created = Group.objects.get_or_create(name=UserGroups.ADMINS)

            if created:
                print(f'Created {UserGroups.ADMINS} group')

            user.groups.add(admins_group)

        return user

    def create_user_without_save(self, email, username, first_name, last_name, password=None, currency="", **extra_fields):
        """
       Create user with the given details, without saving in the database.
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

        # Currency validation - administrators don't need it
        if not is_administrator:
            if not currency:
                raise ValueError("The Currency must be set")

        # Password validation
        if password is None:
            if not is_administrator:
                raise ValueError("The password cannot be empty")
            else:
                # Generate random password for administrators
                password = self.make_random_password()
                # Make sure the admin changes the password on first login
                extra_fields.setdefault("change_password", True)

        # Admin/Super User accounts have to be active by default
        if is_administrator:
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

        return user

    def create_user(self, email, username, first_name, last_name, password=None, currency="", **extra_fields):
        """
        Create and save a user with the given details.
        """
        user = self.create_user_without_save(email, username, first_name, last_name, password, currency, **extra_fields)
        user.save()

        # Assign user to their corresponding permission group.
        self.assign_permission_groups(user)
        user.save()

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