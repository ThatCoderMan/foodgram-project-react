# Generated by Django 2.2.16 on 2022-12-05 18:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodgram', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='title',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.CreateModel(
            name='ShopList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopping_list', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
