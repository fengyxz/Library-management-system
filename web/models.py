from distutils.command.upload import upload
from unittest.util import _MAX_LENGTH
from django.db import models
from django.forms import CharField, IntegerField

# Create your models here.

# 设置管理员表，保存管理员信息
class manager(models.Model):
    id=models.CharField(verbose_name="ID",max_length=32,primary_key=True)
    password=models.CharField(verbose_name="密码",max_length=32)
    name=models.CharField(verbose_name="姓名",max_length=32)
    contact=models.CharField(verbose_name="联系方式",max_length=20)

# 设置图书信息，存储图书信息
class book(models.Model):
    bno=models.CharField(verbose_name="图书编号",max_length=32,primary_key=True)
    type=models.CharField(verbose_name="类别",max_length=20)
    title=models.CharField(verbose_name="书名",max_length=32)
    publisher=models.CharField(verbose_name="出版社",max_length=32)
    author=models.CharField(verbose_name="作者",max_length=32)
    year=models.IntegerField(verbose_name="年份")
    price=models.DecimalField(verbose_name="价格",max_digits=8,decimal_places=2)
    total=models.IntegerField(verbose_name="总藏书量")
    stock=models.IntegerField(verbose_name="当前库存")

# 借书证表，用于管理借书证
class card(models.Model):
    cno=models.CharField(verbose_name="卡号",max_length=32,primary_key=True)
    name=models.CharField(verbose_name="姓名",max_length=32)
    department=models.CharField(verbose_name="部门",max_length=32)

    type_choices=(
        (1,'学生'),
        (2,'教师'),
    )
    type=models.SmallIntegerField(verbose_name="类别",choices=type_choices)

# 文件上传图书入库
class newbooks(models.Model):
    file=models.FileField(verbose_name="上传")

class borrow_list(models.Model):
    book=models.ForeignKey(to="book",to_field="bno",verbose_name="书号",on_delete=models.CASCADE)
    card=models.ForeignKey(to="card",to_field="cno",verbose_name="卡号",on_delete=models.CASCADE)
    borrow_time=models.DateField(verbose_name="借期")
    return_time=models.DateField(verbose_name="预计还期")
    manager=models.ForeignKey(to="manager",to_field="id",verbose_name="经手人",null=True, blank=True, on_delete=models.SET_NULL)