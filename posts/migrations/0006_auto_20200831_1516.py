# Generated by Django 2.2.9 on 2020-08-31 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_profile_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='rating',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Рейтинг публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='profile_author',
            name='image',
            field=models.ImageField(blank=True, help_text='Она будет Вашим символом на этом сайте', null=True, upload_to='posts/', verbose_name='Ваша фотография'),
        ),
    ]
