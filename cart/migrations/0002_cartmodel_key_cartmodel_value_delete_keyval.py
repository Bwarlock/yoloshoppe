# Generated by Django 4.1.7 on 2023-04-05 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartmodel',
            name='key',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='cartmodel',
            name='value',
            field=models.IntegerField(null=True),
        ),
        migrations.DeleteModel(
            name='KeyVal',
        ),
    ]