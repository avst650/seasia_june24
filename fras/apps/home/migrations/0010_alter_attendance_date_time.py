# Generated by Django 4.2.2 on 2023-07-04 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_unknown'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
