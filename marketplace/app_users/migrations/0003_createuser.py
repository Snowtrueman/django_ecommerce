import os
from django.contrib.auth.hashers import make_password
from django.db import migrations


def init_settings(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User_Profile = apps.get_model("app_users", "UserProfile")
    db_alias = schema_editor.connection.alias
    superuser = User.objects.using(db_alias).create(username="admin",
                                                    email="admin@megano.com",
                                                    is_staff=True,
                                                    is_superuser=True,
                                                    password=make_password("123456")
                                                    )

    User_Profile.objects.using(db_alias).create(user=superuser,
                                                role="Admin",
                                                name="Daniil",
                                                surname="Andreyev",
                                                email="dany@megano.com",
                                                phone="9101235478",
                                                city="Moscow",
                                                slug="admin",
                                                )


def reverse_settings(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User_Profile = apps.get_model("app_users", "UserProfile")
    db_alias = schema_editor.connection.alias
    user = User.objects.using(db_alias).filter(username="admin").first()
    User_Profile.objects.using(db_alias).filter(user=user).delete()
    user.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("app_users", "0002_settings_init"),
    ]

    operations = [
        migrations.RunPython(init_settings, reverse_settings),
    ]
