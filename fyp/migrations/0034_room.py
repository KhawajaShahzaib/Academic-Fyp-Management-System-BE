# Generated by Django 4.2.11 on 2025-01-14 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyp', '0033_rename_marks_awarded_groupmarks_marks_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
    ]
