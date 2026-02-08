from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_product_stone_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='material_type',
            field=models.CharField(
                blank=True,
                null=True,
                choices=[('jewelry', 'Ювелирные материалы'), ('other', 'Другие материалы')],
                max_length=20,
                verbose_name='Материалы',
            ),
        ),
    ]
