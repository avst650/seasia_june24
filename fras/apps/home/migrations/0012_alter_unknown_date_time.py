# Generated by Django 4.2.6 on 2024-02-13 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_rejected_unknown'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unknown',
            name='date_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
