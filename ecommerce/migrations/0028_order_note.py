# Generated by Django 3.1.5 on 2021-03-10 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0027_complaint'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='note',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Note'),
        ),
    ]
