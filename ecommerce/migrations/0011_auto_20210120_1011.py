# Generated by Django 3.1.2 on 2021-01-20 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0010_auto_20210117_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('R', 'RECALL'), ('CO', 'Confirmed'), ('CA', 'Canceled'), ('OD', 'On Delivery'), ('D', 'Delivered'), ('R', 'Returned')], default='P', max_length=2, verbose_name='Order Status'),
        ),
        migrations.AlterField(
            model_name='orderstatuschange',
            name='new_status',
            field=models.CharField(choices=[('P', 'Pending'), ('R', 'RECALL'), ('CO', 'Confirmed'), ('CA', 'Canceled'), ('OD', 'On Delivery'), ('D', 'Delivered'), ('R', 'Returned')], max_length=2, verbose_name='New Status'),
        ),
        migrations.AlterField(
            model_name='orderstatuschange',
            name='previous_status',
            field=models.CharField(choices=[('P', 'Pending'), ('R', 'RECALL'), ('CO', 'Confirmed'), ('CA', 'Canceled'), ('OD', 'On Delivery'), ('D', 'Delivered'), ('R', 'Returned')], max_length=2, verbose_name='Previous Status'),
        ),
    ]
