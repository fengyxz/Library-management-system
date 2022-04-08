from dataclasses import field
from django import forms
from logging import PlaceHolder
from django.http import HttpResponse
from django.shortcuts import redirect, render
from web import models
import re

# Create your views here.
# 开始界面


def start(request):
    if request.method == 'GET':
        return render(request, 'start.html')

# 对管理员账户的验证写在 account.py

# 进入管理员界面


def manager(request):
    # 在缓存中获取登录后管理员的信息
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    return render(request, 'manager.html', {"name": name})

# 管理借书证界面--管理员操作


def manager_card(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]

    # 获取POST的操作中输入的借书证id--定义为nid
    nid = request.POST.get("nid")
    # 如果没有获取到nid，nid为空
    if (not nid):
        nid = ""
        queryset = models.card.objects.all()
        return render(request, 'manager_card.html', {"queryset": queryset, "name": name, "nid": nid})
    # 获取到nid，在table card中根据cno去搜索相应的借书证
    queryset = models.card.objects.filter(cno=nid)
    if queryset:
        # 如果有该借书证，则将该cno存储到缓存中，nid=该cno
        request.session["info"]["nid"] = nid
        request.session.set_expiry(60 * 60 * 24 * 7)
        print(request.session["info"])
        return render(request, 'manager_card.html', {"queryset": queryset, "name": name, "nid": nid})
    # 没有该借书证，报错
    else:
        return render(request, 'manager_card.html', {"error_msg": "无该借书证，请检查", "name": name, "nid": nid})

# 删除借书证--管理员操作


def manager_card_delete(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.GET.get('nid')
    print(nid)
    # 在card中找到该cno对应的card，然后删除
    models.card.objects.filter(cno=nid).delete()
    return redirect('/manager/card/', {"name": name})


#添加借书证的属性和table card中的属性一致，可以使用Modelform生成表单
##################   创建Modelform：借书证   ##################


class CardModelform(forms.ModelForm):
    class Meta:
        model = models.card
        fields = '__all__'

    # 将生成的ModelForm中的生成的widget属性改为form-control
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}

# 添加借书证--管理员操作


def manager_card_add(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    if request.method == "GET":
        form = CardModelform()
        return render(request, 'manager_card_add.html', {"form": form, "name": name})

    # 管理员POST提交数据，进行数据校验
    form = CardModelform(data=request.POST)
    if form.is_valid():
        # 如果输入的数据合理，校验成功，则保存到table card
        form.save()
        return redirect('/manager/card/')

    # 如果输入的数据不合理，则在原有界面上报错，同时保留已输入的form数据
    return render(request, 'manager_card_add.html', {"form": form, "name": name})

# 图书入库界面


def book_add(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    return render(request, 'book_add.html', {"name": name})

#############   创建Modelform：图书信息   ###############


class BookModelform(forms.ModelForm):
    num = forms.IntegerField(label='数量')
    book_id = forms.CharField(label='书号')

    class Meta:
        model = models.book
        # 改变一下field的顺序，调整表单输入栏目顺序
        fields = ['book_id', 'type', 'title',
                  'publisher', 'author', 'year', 'price', 'num']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}

# 单本入库


def book_add_one(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    form = BookModelform()
    if request.method == "GET":
        return render(request, 'book_add_one.html', {"form": form, "name": name})
    # 管理员POST提交数据，进行数据校验
    data = request.POST
    form = BookModelform(data=request.POST)
    bno = data['book_id']
    if form.is_valid():
        obj = models.book.objects.filter(bno=bno)
        if obj:
            print(data['num'])
            row_object = obj[0]
            row_object.stock = row_object.stock+int(data['num'])
            row_object.total = row_object.total+int(data['num'])
            row_object.save()
        else:
            models.book.objects.create(bno=bno, type=data['type'], title=data['title'], publisher=data['publisher'],
                                       year=data['year'], author=data['author'], price=data['price'], total=data['num'], stock=data['num'])
            # print(newbooks)
        return redirect('/book/add/suc/', {"name": name})
    return render(request, 'book_add_one.html', {"form": form, "name": name})

# 入库成功


def book_add_suc(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    if request.method == "GET":
        return render(request, 'book_add_suc.html')
    # POST操作，返回添加页面
    return redirect('/book/add/', {"name": name})

# 批量入库


def book_add_multi(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    # GET时跳转至界面
    if(request.method == "GET"):
        return render(request, 'book_add_multi.html')
    # POST操作时，得到上传的文件newbooks
    file_object = request.FILES.get("newbooks")
    #print(file_object)
    if(not file_object):
        return render(request, 'book_add_multi.html', {"name": name, "error_msg": "不得上传为空"})
    name=file_object.name
    type=name[name.rfind('.'):]
    print(type)
    if(type != '.txt'):
        return render(request, 'book_add_multi.html', {"name": name, "error_msg": "仅支持txt文件，请重新上传"})
    file = file_object.read()
    # 将其转化为字符串形式
    str = file.decode('utf-8')

    # 通过正则表达式，得到（ ）内的字符串，生成列表list
    list = re.findall(r'[(](.*?)[)]', str)

    querysetlist = []
    # 对list中的每一个字符串进行字符串切割，切割','
    for obj in list:
        data = obj.split(', ')
        print(data)
        book = models.book.objects.filter(bno=data[0])
        if book:
            # 如果新添加的图书的bno已经存在，直接修改库存
            row_object = book[0]
            row_object.stock = row_object.stock+int(data[7])
            row_object.total = row_object.total+int(data[7])
            row_object.save()
        else:
            # 如果不存在，则需要创建
            querysetlist.append(models.book(bno=data[0], type=data[1], title=data[2], publisher=data[3], year=int(
                data[4]), author=data[5], price=float(data[6]), total=int(data[7]), stock=int(data[7])))
    # 批量创建不存在的图书目录
    models.book.objects.bulk_create(querysetlist)
    return redirect('/book/add/suc/', {"name": name})

# 图书查询列表，通过get得到传递的参数


def book_list(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    # 一开始知识储备不足，为了减少出错，选择手动写循环,但其实后来发现本身data=request.GET 可以得到字典来获取GET的数据
    # 但该方法也可以作为一种选择，就不做修改了
    search_b = request.GET.get('b', "")
    search_t = request.GET.get('t', "")
    search_a = request.GET.get('a', "")
    search_p = request.GET.get('p', "")
    search_pl = request.GET.get('pl', "")
    search_pr = request.GET.get('pr', "")
    search_yl = request.GET.get('yl', "")
    search_yr = request.GET.get('yr', "")
    order = request.GET.get('order', "")

    # 通过得到的order来进行排序
    if order == 'bno_1' or (not order):
        res = models.book.objects.all().order_by('bno')
    if order == 'bno_2':
        res = models.book.objects.all().order_by('-bno')
    if order == 'year_1':
        res = models.book.objects.all().order_by('year')
    if order == 'year_2':
        res = models.book.objects.all().order_by('-year')
    if order == 'title_1':
        res = models.book.objects.all().order_by('title')
    if order == 'title_2':
        res = models.book.objects.all().order_by('-title')
    if order == 'year_1':
        res = models.book.objects.all().order_by('year')
    if order == 'year_2':
        res = models.book.objects.all().order_by('-year')
    if order == 'price_1':
        res = models.book.objects.all().order_by('price')
    if order == 'price_2':
        res = models.book.objects.all().order_by('-price')
    if order == 'stock_1':
        res = models.book.objects.all().order_by('stock')
    if order == 'stock_2':
        res = models.book.objects.all().order_by('-stock')
    if order == 'total_1':
        res = models.book.objects.all().order_by('total')
    if order == 'total_2':
        res = models.book.objects.all().order_by('-total')

    # 对关键字进行筛选
    if search_b:
        res = res.filter(bno__contains=search_b)
    if search_t:
        res = res.filter(title__contains=search_t)
    if search_a:
        res = res.filter(author__contains=search_a)
    if search_p:
        res = res.filter(publisher__contains=search_p)
    if search_pl:
        res = res.filter(price__gte=search_pl)
    if search_pr:
        res = res.filter(price__lte=search_pr)
    if search_yl:
        res = res.filter(year__gte=search_yl)
    if search_yr:
        res = res.filter(year__lte=search_yr)

    # 筛选出前50条数据
    res = res.all()[:50]

    return render(request, 'book_list.html', {"name": name, "queryset": res, "search_t": search_t, "search_a": search_a, "search_p": search_p, "search_pl": search_pl, "search_pr": search_pr, "search_yl": search_yl, "search_yr": search_yr, "order": order})


# 借阅图书--管理员操作（管理员信息存于cookies）
#########   创建form：借书记录   ###############
class Borrowform(forms.Form):
    bno = forms.CharField(
        label="书号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    borrow_date = forms.DateField(
        label="借期(YYYY-MM-DD)",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    return_date = forms.DateField(
        label="预计还期(YYYY-MM-DD)",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )


# 借阅图书--管理员操作
def book_borrow(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.session["info"]["nid"]
    if request.method == "GET":
        form = Borrowform()
        return render(request, 'book_borrow.html', {"form": form, "name": name, "nid": nid})

    # 管理员POST提交数据，进行数据校验
    form = Borrowform(data=request.POST)
    if form.is_valid():
        # 输入的数据符合Modelsform的规定格式
        data = form.cleaned_data
        # 查询是否存在输入的bno的图书
        borrow_book = models.book.objects.filter(bno=data['bno'])
        if borrow_book:
            # 存在该图书
            the_book = models.book.objects.filter(bno=data['bno'])[0]

        if (not borrow_book):
            return render(request, 'book_borrow.html', {"form": form, "error_msg": "该图书不存在，请检查", "name": name, "nid": nid})
        elif the_book.stock <= 0:
            # 该书库存不足，去寻找预计归还时间最早的
            earliest_books = models.borrow_list.objects.filter(
                book_id=data['bno']).order_by("return_time")
            if earliest_books:
                earliest_book = earliest_books[0]
                return render(request, 'book_borrow.html', {"form": form, "name": name, "nid": nid, "error_msg": "库存不足，借阅失败,预计最快归还时间: ", "date": earliest_book.return_time})
            else:
                return render(request, 'book_borrow.html', {"form": form, "error_msg": "该图书无库存，请检查", "name": name, "nid": nid})
        else:
            # 借阅成功，触发器：该图书的库存-1
            the_book.stock -= 1
            the_book.save()
            models.borrow_list.objects.create(
                book_id=data['bno'], card_id=nid, manager_id=id, borrow_time=data['borrow_date'], return_time=data['return_date'])
            return render(request, 'book_borrow.html', {"form": form, "suc_msg": "借阅成功", "name": name, "nid": nid})
    # 输入数据有误（不符合form）
    return render(request, 'book_borrow.html', {"form": form, "name": name, "nid": nid})


# 归还图书--管理员操作（管理员信息存于cookies）
#########   创建form：还书信息   ###############
class Returnform(forms.Form):
    bno = forms.CharField(
        label="书号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

def book_return(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.session["info"]["nid"]

    if request.method == "GET":
        form = Returnform()
        return render(request, 'book_return.html', {"form": form, "name": name, "nid": nid})
    # POST操作，得到提交的数据
    form = Returnform(data=request.POST)
    if form.is_valid():
        data = form.cleaned_data
        bno = data['bno']
        cno = nid
        # 检验借阅信息是否合理
        info = models.borrow_list.objects.filter(book_id=bno, card_id=cno)
        # 存在该条借阅记录，进行归还，触发器：库存+1
        if info:
            obj = info[0]
            obj.delete()
            the_book = models.book.objects.filter(bno=data['bno'])[0]
            the_book.stock += 1
            the_book.save()
            return render(request, 'book_return.html', {"form": form, "suc_msg": "归还成功", "name": name, "nid": nid})
        else:
            # 不存在该条记录
            return render(request, 'book_return.html', {"form": form, "suc_msg": "归还失败，该书不存在该借书证借阅列表中", "name": name, "nid": nid})
    return render(request, 'book_return.html', {"form": form, "name": name, "nid": nid})


# 将借书、还书整合在一起，实现对所借图书的查询
def book_modify(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    # GET操作，同时清楚原保留的借书证信息
    if request.method == "GET":
        request.session["info"]["nid"] = ""
        request.session.set_expiry(60 * 60 * 24 * 7)
        return render(request, 'book_modify.html', {'name': name})

    # POST操作，得到输入的借书证信息
    nid = request.POST.get("nid")
    card = models.card.objects.filter(cno=nid)

    if card:
        # 如果借书证存在，则返回借阅的图书信息，同时将借书证号存于缓存，用于之后归还和借阅，免除重新输入借书证号
        books = models.borrow_list.objects.filter(
            card_id=nid).order_by('book_id')
        request.session["info"]["nid"] = nid
        request.session.set_expiry(60 * 60 * 24 * 7)
        print(request.session["info"])

        queryset = []
        for obj in books:
            queryset.append(models.book.objects.get(bno=obj.book_id))
        return render(request, 'book_modify.html', {"queryset": queryset, "name": name, "nid": nid})
    else:
        # 借书证不存在，报错
        return render(request, 'book_modify.html', {"error_msg": "无该借书证，请检查", "name": name, "nid": nid})
