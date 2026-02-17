from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0025_homepageheroimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroBlock',
            fields=[],
            options={
                'verbose_name': 'Hero главной страницы',
                'verbose_name_plural': 'Hero главной страницы',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('catalog.homepageblock',),
        ),
    ]
