# Generated by Django 4.0.3 on 2022-04-04 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_rename_name_book_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='card',
            fields=[
                ('cno', models.IntegerField(primary_key=True, serialize=False, verbose_name='卡号')),
                ('name', models.CharField(max_length=32, verbose_name='姓名')),
                ('department', models.CharField(max_length=32, verbose_name='部门')),
                ('type', models.SmallIntegerField(choices=[(1, '学生'), (2, '教师')], verbose_name='类别')),
            ],
        ),
    ]
