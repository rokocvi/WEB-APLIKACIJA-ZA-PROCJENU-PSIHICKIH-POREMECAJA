# Generated by Django 5.2.1 on 2025-05-26 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mindapp', '0002_lijecnik_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lijecnik',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
