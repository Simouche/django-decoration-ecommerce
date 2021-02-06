# Generated by Django 3.1.2 on 2021-02-04 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0020_product_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='free_shipping',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('RC', 'RECALL'), ('CO', 'Confirmed'), ('CA', 'Canceled'), ('OD', 'On Delivery'), ('D', 'Delivered'), ('R', 'Returned'), ('RE', 'Refund'), ('PA', 'Paid'), ('NA', 'No Answer')], default='P', max_length=2, verbose_name='Order Status'),
        ),
        migrations.AlterField(
            model_name='orderstatuschange',
            name='new_status',
            field=models.CharField(choices=[('P', 'Pending'), ('RC', 'RECALL'), ('CO', 'Confirmed'), ('CA', 'Canceled'), ('OD', 'On Delivery'), ('D', 'Delivered'), ('R', 'Returned'), ('RE', 'Refund'), ('PA', 'Paid'), ('NA', 'No Answer')], max_length=2, verbose_name='New Status'),
        ),
        migrations.AlterField(
            model_name='orderstatuschange',
            name='previous_status',
            field=models.CharField(choices=[('P', 'Pending'), ('RC', 'RECALL'), ('CO', 'Confirmed'), ('CA', 'Canceled'), ('OD', 'On Delivery'), ('D', 'Delivered'), ('R', 'Returned'), ('RE', 'Refund'), ('PA', 'Paid'), ('NA', 'No Answer')], max_length=2, verbose_name='Previous Status'),
        ),
    ]
