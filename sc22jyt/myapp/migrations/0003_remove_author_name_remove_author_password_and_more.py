# Generated by Django 5.0.3 on 2024-03-21 02:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_author_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='name',
        ),
        migrations.RemoveField(
            model_name='author',
            name='password',
        ),
        migrations.RemoveField(
            model_name='author',
            name='username',
        ),
    ]
