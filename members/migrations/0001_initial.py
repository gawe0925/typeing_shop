# Generated by Django 4.0.4 on 2022-08-07 07:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('default_address', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Default Shipping Address')),
                ('city', models.CharField(max_length=20, null=True, verbose_name='City')),
                ('post_code', models.CharField(max_length=6, null=True, verbose_name='Post Code')),
                ('user_image', models.ImageField(upload_to='templates/user_pictures')),
            ],
            options={
                'verbose_name': 'Member Header',
                'verbose_name_plural': 'Member Header',
            },
            bases=('base.user',),
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]