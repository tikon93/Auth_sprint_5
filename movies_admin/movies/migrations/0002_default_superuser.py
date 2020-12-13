import logging
from typing import Optional

from decouple import config
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations

logger = logging.getLogger(__name__)
default_username: Optional[str] = config("DJANGO_DEFAULT_SUPERUSER", default=None)
default_password: Optional[str] = config("DJANGO_DEFAULT_PASSWORD", default=None)


def create_default_user(apps, schema_editor):
    if default_username is not None and default_password is not None:
        if len(User.objects.filter(username=default_username)) == 0:
            logger.info("Creating default superuser")
            User.objects.create_superuser(username=default_username, email='', password=default_password)
        else:
            logger.info("Default superuser already exists, do nothing")


def delete_default_user(apps, schema_editor):
    if default_username is not None and default_password is not None:
        try:
            u = User.objects.get(username=default_username)
            u.delete()
        except ObjectDoesNotExist:
            logger.error(f"User {default_username} doesn't exist, do nothing")


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_user, delete_default_user)
    ]
