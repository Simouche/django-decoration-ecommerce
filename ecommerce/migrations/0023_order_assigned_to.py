# Generated by Django 3.1.2 on 2021-02-16 14:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ecommerce', '0022_auto_20210208_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Assigned To'),
        ),
    ]
