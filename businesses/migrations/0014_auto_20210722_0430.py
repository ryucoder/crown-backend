# Generated by Django 3.1.4 on 2021-07-22 04:30

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0013_order_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessConnect',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('dentist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dentists', to='businesses.business')),
                ('laboratory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='laboratories', to='businesses.business')),
            ],
            options={
                'verbose_name': 'Business Connect',
                'verbose_name_plural': 'Business Connects',
            },
        ),
        migrations.AddField(
            model_name='business',
            name='connected_businesses',
            field=models.ManyToManyField(blank=True, related_name='business', through='businesses.BusinessConnect', to='businesses.Business'),
        ),
    ]
