from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_product_size_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stone_option',
            field=models.CharField(
                blank=True,
                null=True,
                choices=[('with_stones', 'С Камнями'), ('without_stones', 'Без камней')],
                max_length=20,
                verbose_name='Камни',
            ),
        ),
    ]
