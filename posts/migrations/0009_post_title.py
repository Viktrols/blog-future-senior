# Generated by Django 2.2.6 on 2021-03-28 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_follow'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.TextField(blank=True, max_length=100, null=True, verbose_name='Текст'),
        ),
    ]
