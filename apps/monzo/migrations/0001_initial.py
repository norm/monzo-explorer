# Generated by Django 3.0.6 on 2020-05-20 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('group_id', models.CharField(blank=True, max_length=64, null=True)),
                ('name', models.CharField(max_length=128)),
                ('logo', models.URLField()),
                ('address', models.CharField(blank=True, max_length=1024, null=True)),
                ('postcode', models.CharField(blank=True, max_length=16, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True)),
                ('twitter_id', models.CharField(blank=True, max_length=16, null=True)),
                ('foursquare_id', models.CharField(blank=True, max_length=16, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
                ('description', models.CharField(blank=True, max_length=128, null=True)),
                ('amount', models.IntegerField()),
                ('currency', models.CharField(max_length=10)),
                ('notes', models.CharField(blank=True, max_length=128, null=True)),
                ('category', models.CharField(blank=True, max_length=64, null=True)),
                ('settled', models.DateTimeField(blank=True, null=True)),
                ('local_amount', models.IntegerField()),
                ('local_currency', models.CharField(max_length=10)),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('declined', models.BooleanField(default=False)),
                ('decline_reason', models.CharField(blank=True, max_length=128, null=True)),
                ('card_check', models.BooleanField(default=False)),
                ('scheme', models.CharField(max_length=64)),
                ('merchant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='monzo.Merchant')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
