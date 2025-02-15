# Generated by Django 4.2.11 on 2024-10-01 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fyp', '0018_delete_specialty'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMeeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('status', models.CharField(choices=[('Upcoming', 'Upcoming'), ('Past', 'Past')], max_length=20)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='fyp.group')),
            ],
        ),
        migrations.DeleteModel(
            name='Meeting',
        ),
    ]
