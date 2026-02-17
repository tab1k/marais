from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0026_heroblock_proxy'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepageheroimage',
            name='link_url',
            field=models.CharField(blank=True, max_length=500, verbose_name='Ссылка'),
        ),
    ]
