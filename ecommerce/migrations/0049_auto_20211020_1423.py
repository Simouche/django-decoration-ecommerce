# Generated by Django 3.1.5 on 2021-10-20 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0048_auto_20211006_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='plaintes', to='ecommerce.order', verbose_name='Order'),
        ),
    ]
