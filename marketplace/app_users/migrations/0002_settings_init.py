import os
from django.db import migrations
import environ
from marketplace.settings import BASE_DIR


def init_settings(apps, schema_editor):
    env = environ.Env()
    print(BASE_DIR)
    environ.Env.read_env(os.path.join(BASE_DIR, "marketplace/.env.settings"))
    Settings = apps.get_model("app_users", "Settings")
    db_alias = schema_editor.connection.alias
    print(env("GENERAL_PHONE"))
    Settings.objects.using(db_alias).create(general_phone=env("GENERAL_PHONE"),
                                            general_email=env("GENERAL_EMAIL"),
                                            general_address=env("GENERAL_ADDRESS"),
                                            facebook_url=env("FACEBOOK_URL"),
                                            twitter_url=env("TWITTER_URL"),
                                            linkedin_url=env("LINKEDIN_URL"),
                                            pinterest_url=env("PINTEREST_URL"),
                                            product_cache_time=env("PRODUCT_CACHE_TIME"),
                                            ordinary_delivery_price=env("ORDINARY_DELIVERY_PRICE"),
                                            express_delivery_price=env("EXPRESS_DELIVERY_PRICE"),
                                            delivery_sum_to_free=env("DELIVERY_SUM_TO_FREE")
                                            )


def reverse_settings(apps, schema_editor):
    Settings = apps.get_model("app_users", "Settings")
    db_alias = schema_editor.connection.alias
    Settings.objects.using(db_alias).all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("app_users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(init_settings, reverse_settings),
    ]
