# Generated by Django 3.2.5 on 2021-08-12 08:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatsFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('date_start', models.DateTimeField(blank=True, null=True)),
                ('date_end', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddField(
            model_name='wallet',
            name='limit_currency',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='limit_native',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='limit_tokens',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='native_transfer',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='nft_transfer',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='wallet',
            name='token_transfer',
            field=models.BooleanField(default=True),
        ),
        migrations.DeleteModel(
            name='Filter',
        ),
        migrations.AddField(
            model_name='statsfilter',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='wallets.wallet'),
        ),
        migrations.AlterUniqueTogether(
            name='statsfilter',
            unique_together={('address', 'wallet')},
        ),
    ]