from django.db import migrations


def generate_admin(apps, schema_editor):
    from django.contrib.auth import get_user_model

    USERNAME = "admin1"
    EMAIL = "admin@user.com"
    FIRST_NAME = "John"
    LAST_NAME = "Doe"
    PASSWORD = "admin1"

    user = get_user_model()

    if not user.objects.filter(username=USERNAME, email=EMAIL).exists():
        print("Creating new administrator")
        admin = user.objects.create_user(email=EMAIL, username=USERNAME, first_name=FIRST_NAME, last_name=LAST_NAME, password=PASSWORD, is_admin=True)
        admin.save()
    else:
        print("Administrator already created!")


def generate_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model

    USERNAME = "super1"
    EMAIL = "super@user.com"
    FIRST_NAME = "John"
    LAST_NAME = "Doe"
    PASSWORD = "super1"

    user = get_user_model()

    if not user.objects.filter(username=USERNAME, email=EMAIL).exists():
        print("Creating new superuser")
        superuser = user.objects.create_superuser(email=EMAIL, username=USERNAME, first_name=FIRST_NAME, last_name=LAST_NAME, password=PASSWORD)
        superuser.save()
    else:
        print("Superuser already created!")


class Migration(migrations.Migration):
    dependencies = [("register", "0002_customuser_change_password")]

    operations = [migrations.RunPython(generate_superuser), migrations.RunPython(generate_admin)]