# Generated by Django 4.0.3 on 2022-04-04 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_alter_card_cno'),
    ]

    operations = [
        migrations.CreateModel(
            name='newbooks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='newbooks/', verbose_name='上传')),
            ],
        ),
        migrations.AlterField(
            model_name='book',
            name='stock',
            field=models.IntegerField(verbose_name='当前库存'),
        ),
        migrations.AlterField(
            model_name='book',
            name='total',
            field=models.IntegerField(verbose_name='总藏书量'),
        ),
        migrations.AlterField(
            model_name='book',
            name='year',
            field=models.IntegerField(verbose_name='年份'),
        ),
        migrations.AlterField(
            model_name='card',
            name='cno',
            field=models.IntegerField(primary_key=True, serialize=False, verbose_name='卡号'),
        ),
    ]
