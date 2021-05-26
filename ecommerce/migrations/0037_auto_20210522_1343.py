# Generated by Django 3.1.5 on 2021-05-22 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0036_auto_20210505_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='ai',
            field=models.CharField(blank=True, max_length=255, verbose_name='AI'),
        ),
        migrations.AddField(
            model_name='settings',
            name='nif',
            field=models.CharField(blank=True, max_length=255, verbose_name='NIF'),
        ),
        migrations.AddField(
            model_name='settings',
            name='rc',
            field=models.CharField(blank=True, max_length=255, verbose_name='RC'),
        ),
    ]