# Generated by Django 2.2.16 on 2023-04-09 21:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created', 'id'), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
    ]