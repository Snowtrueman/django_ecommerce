# Generated by Django 4.1.4 on 2023-04-15 20:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('title', models.CharField(max_length=50, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('sort_index', models.IntegerField(default=1, verbose_name='Индекс сортировки')),
                ('icon', models.FileField(null=True, upload_to='category_pictures', verbose_name='Иконка')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='URL')),
                ('selected', models.BooleanField(default=False, verbose_name='Избранная категория')),
                ('img', models.ImageField(blank=True, null=True, upload_to='categories', verbose_name='Картинка')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='app_goods.categories', verbose_name='Родительская категория')),
            ],
            options={
                'verbose_name': 'Категория товаров',
                'verbose_name_plural': 'Категории товаров',
                'ordering': ('sort_index',),
            },
        ),
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('part_num', models.IntegerField(verbose_name='Артикул')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('short_description', models.CharField(max_length=255, verbose_name='Короткое Описание')),
                ('description', models.TextField(verbose_name='Полное описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Цена')),
                ('amount', models.IntegerField(verbose_name='Остаток')),
                ('free_delivery', models.BooleanField(default=False, verbose_name='Бесплатная доставка')),
                ('sort_index', models.IntegerField(default=1, verbose_name='Индекс сортировки')),
                ('limited', models.BooleanField(default=False, verbose_name='Спецпредложение')),
                ('is_published', models.BooleanField(default=True, verbose_name='Опубликовано')),
                ('date_published', models.DateField(auto_now=True, verbose_name='Дата публикации')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goods', to='app_goods.categories', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'ordering': ('date_published',),
            },
        ),
        migrations.CreateModel(
            name='Params',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Название характеристики')),
                ('main', models.BooleanField(default=True, verbose_name='Основной параметр')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='params', to='app_goods.categories', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Параметр товаров',
                'verbose_name_plural': 'Параметры товаров',
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
                ('date_published', models.DateTimeField(auto_now=True, verbose_name='Дата публикации')),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='app_goods.goods', verbose_name='Товар')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_reviews', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ('date_published',),
            },
        ),
        migrations.CreateModel(
            name='ImageGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='goods', verbose_name='Картинка')),
                ('main', models.BooleanField(default=False, verbose_name='Главное изображение')),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app_goods.goods', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Галерея',
                'verbose_name_plural': 'Галерея',
                'ordering': ('-main',),
            },
        ),
        migrations.AddField(
            model_name='goods',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='goods_with_tag', to='app_goods.tags', verbose_name='Теги'),
        ),
        migrations.CreateModel(
            name='ParamValues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('value', models.CharField(max_length=255, verbose_name='Значение характеристики')),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='params', to='app_goods.goods', verbose_name='Товар')),
                ('param', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='app_goods.params', verbose_name='Характеристика')),
            ],
            options={
                'verbose_name': 'Значение характиристики',
                'verbose_name_plural': 'Значения характеристик',
                'unique_together': {('good', 'param', 'value')},
            },
        ),
    ]