from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0024_merge_20260211'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomepageHeroImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='blocks/hero/', verbose_name='Изображение')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('block', models.ForeignKey(limit_choices_to={'block_type': 'hero'}, on_delete=django.db.models.deletion.CASCADE, related_name='hero_images', to='catalog.homepageblock', verbose_name='Hero блок')),
            ],
            options={
                'verbose_name': 'Изображение для Hero',
                'verbose_name_plural': 'Изображения для Hero',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
