from django.shortcuts import render, HttpResponse, redirect
from django import forms
from io import BytesIO

from web import models

class LoginForm(forms.Form):
    id = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class":"form-control"})
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"class":"form-control"})
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
    

def login(request):
    """ 登录 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        data=request.POST
        # 验证成功，获取到的用户名和密码

        # 去数据库校验用户名和密码是否正确，获取用户对象、None
        admin_object = models.manager.objects.filter(id=data['id'],password=data['password']).first()
        print(admin_object)
        if not admin_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, 'login.html', {'form': form})

        # # id和密码正确
        # # 网站生成随机字符串; 写到用户浏览器的cookie中；在写入到session中；
        request.session["info"] = {'id': admin_object.id, 'name': admin_object.name,'nid':""}
        # session可以保存7天
        request.session.set_expiry(60 * 60 * 24 * 7)

        return redirect("/book/list/")

    return render(request, 'login.html', {'form': form})



def logout(request):
    """ 注销 """
    request.session.clear()
    return redirect('/start/')