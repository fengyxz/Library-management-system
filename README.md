# 图书管理系统
**采用Django+Mysql完成**

默认已经安装：Python3.9 + Mysql

1. 创建database：命名为booksystem
2. 配置Mysql接口：
在settings文件中修改用户名和密码，之后运行

```
python3.9 manage.py makemigrations
python3.9 manage.py migrate
```
3. 运行请输入：
`python3.9 manage.py runserver 0.0.0.0:8000`
4. 显示创建成功后，浏览器转入`0.0.0.0:8000/start/`即可进入登陆界面
