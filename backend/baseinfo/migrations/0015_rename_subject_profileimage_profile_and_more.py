# Generated by Django 4.1.1 on 2022-10-25 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseinfo', '0014_subjectimage_profileimage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profileimage',
            old_name='subject',
            new_name='profile',
        ),
        migrations.AlterField(
            model_name='profileimage',
            name='image',
            field=models.ImageField(upload_to='profile/images'),
        ),
    ]