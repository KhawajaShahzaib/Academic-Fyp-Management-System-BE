# Generated by Django 4.2.11 on 2024-09-30 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fyp', '0011_remove_assessment_semester_assessment_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='clo',
            name='title',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
