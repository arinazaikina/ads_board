# Generated by Django 4.2 on 2023-09-19 20:08

import app_users.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_users", "0002_alter_customuser_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="first_name",
            field=models.CharField(max_length=64, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_name",
            field=models.CharField(max_length=64, verbose_name="Фамилия"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="phone",
            field=models.CharField(
                max_length=16,
                validators=[app_users.validators.phone_validator],
                verbose_name="Телефон",
            ),
        ),
    ]