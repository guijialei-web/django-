import json
import os
import random
from datetime import datetime
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse
from django.utils.safestring import mark_safe
from staff.utils.bootstrapform import BootStrapForm, BootStrapModelForm
from staff.utils.encrypt import md5
from staff import models
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from staff.utils.code import check_code


# Create your views here.
from staffsystem import settings


def depart_list(request):
    '''部门列表'''
    queryset = models.Department.objects.all()
    queryset = [vars(obj) for obj in queryset]
    # print(queryset)
    queryset1=[]
    for i in queryset:
        values = list(i.items())[1:]
        queryset1.append(values)
    print(queryset1)
        # for value in values:
        #     print(value[1])

    # for i in queryset:
    #     for j in i.__dict__.items():
    #         print(j)
    return render(request, 'depart_list.html', {'queryset1': queryset1})


def depart_add(request):
    '''添加部门'''
    if request.method == 'GET':
        return render(request, 'depart_add.html')
    title = request.POST.get('title')
    models.Department.objects.create(title=title)
    return redirect("/depart/list")


def depart_delete(request):
    '''删除部门'''
    nid = request.GET.get('nid')
    models.Department.objects.filter(id=nid).delete()
    return redirect("/depart/list")


def depart_edit(request, nid):
    '''编辑部门'''
    if request.method == 'GET':
        data = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {"data": data})
    title = request.POST.get('title')
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/list")


def user_list(request):
    '''用户列表'''
    # 获取用户信息

    queryset = models.UserInfo.objects.all()
    for obj in queryset:
        # obj.depart  根据id自动去关联的表中获取那一行的对象
        print(obj.id, obj.creat_time.strftime('%Y-%m-%d'), obj.get_gender_display(), obj.depart.title)
    return render(request, 'user_list.html', {'queryset': queryset})


class UserModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'age', 'account', 'creat_time', 'depart', 'gender']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.TextInput(attrs={"class": "form-control"}),
            "age": forms.TextInput(attrs={"class": "form-control"}),
            "account": forms.TextInput(attrs={"class": "form-control"}),
            "creat_time": forms.DateTimeInput(attrs={"class": "form-control"}),
            "depart": forms.Select(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"})
        }


def user_add(request):
    # 添加用户
    if request.method == 'GET':
        form = UserModelForm()
        return render(request, 'user_add.html', {"form": form})
    form = UserModelForm(data=request.POST)  # 把数据传给ta
    if form.is_valid():
        form.save()  # 保存到数据库
        return redirect('/user/list')
    return render(request, 'user_add.html', {"form": form})


def user_edit(request, nid):
    # 编辑用户
    if request.method == 'GET':
        row_data = models.UserInfo.objects.filter(id=nid).first()
        form = UserModelForm(instance=row_data)
        return render(request, 'user_edit.html', {"form": form})

    row_data = models.UserInfo.objects.filter(id=nid).first()
    form = UserModelForm(data=request.POST, instance=row_data)  # 这里表示把数据更新到这里
    if form.is_valid():
        # 默认是保存用户输入的值，如果想要在用户输入以外的值进行保存
        # form.instance.字段名=值
        form.save()
        return redirect('/user/list')
    return render(request, 'user_edit.html', {'form': form})


def user_delete(request, nid):
    # 删除用户
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('/user/list')


class PrettyModelFrom(forms.ModelForm):
    '''验证方式1'''

    # mobile=forms.CharField(
    #     label='手机号',
    #     validators=[RegexValidator(r'^1[3-9]\d{9}$','电话号码格式错误')]
    # )
    class Meta:
        model = models.PrettyNum
        # fields="__all__"    表示支持所有字段
        # exclude=['level']   排除某个字段

        fields = ['mobile', 'price', 'level', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

    '''验证方式2'''

    def clean_mobile(self):
        txt_mobile = self.cleaned_data['mobile']
        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手机号已经存在')

        return txt_mobile


class PrettyEditModelFrom(BootStrapModelForm):
    '''验证方式1'''

    # 这样可以让手机号不可修改
    # mobile=forms.CharField(disabled=True,label='手机号')
    class Meta:
        model = models.PrettyNum
        # fields="__all__"    表示支持所有字段
        # exclude=['level']   排除某个字段

        fields = ['mobile', 'price', 'level', 'status']

    '''验证方式2'''

    def clean_mobile(self):
        # self.instance.pk可以获取当前编辑的id

        txt_mobile = self.cleaned_data['mobile']
        # 排除id等于自身
        exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手机号已经存在')
        if len(txt_mobile) != 11:
            raise ValidationError('格式错误')
        return txt_mobile


def pretty_list(request):
    # select*from 表 by level desc
    '''靓号列表'''

    search_data = request.GET.get("q", "")
    data = {}
    if search_data:
        data['mobile__contains'] = search_data
    # 根据page参数计算起始位置和结束位置
    page = int(request.GET.get('page', '1'))
    page_size = 10
    start = (page - 1) * page_size
    end = page * page_size

    total_count = models.PrettyNum.objects.filter(**data).order_by('-level').count()
    queryset = models.PrettyNum.objects.filter(**data).order_by('-level')[start:end]
    total_page_count, div = divmod(total_count, page_size)
    if div:
        total_page_count += 1

    # 根据计算，显示前五页后五页
    plus = 5
    if total_page_count < plus * 2 + 1:
        # 数据库数据比较少 ，只显示11页
        start_page = 1
        end_page = plus * 2 + 1
    else:
        # 小的极值  小于5页
        if page < plus:
            start_page = 1
            end_page = plus * 2 + 1
        else:
            # 当前页面加5超过最大页数了
            if page + plus > total_page_count:
                start_page = total_page_count - plus * 2
                end_page = total_page_count + 1
            else:
                start_page = page - plus
                end_page = page + plus + 1
    # 页码
    page_str_list = []
    # 首页
    page_str_list.append('<li><a href="?page=1">首页</a></li>')
    # 上一页
    if page > 1:
        prev = f'<li><a href="?page={page - 1}">上一页</a></li>'
    else:
        prev = '<li><a href="?page=1">上一页</a></li>'
    page_str_list.append(prev)

    # 页面
    for i in range(start_page, end_page):
        if i == page:
            ele = f'<li class="active"><a href="?page={i}">{i}</a></li>'
        else:
            ele = f'<li ><a href="?page={i}">{i}</a></li>'
        page_str_list.append(ele)

        # 上一页
    if page < total_page_count:
        prev = f'<li><a href="?page={page + 1}">下一页</a></li>'
    else:
        prev = f'<li><a href="?page={total_page_count}">下一页</a></li>'
    page_str_list.append(prev)
    # 尾页
    page_str_list.append(f'<li><a href="?page={total_page_count}">首页</a></li>')

    page_string = mark_safe("".join(page_str_list))
    return render(request, 'pretty_list.html',
                  {'queryset': queryset, "search_data": search_data, "page_string": page_string})


def pretty_add(request):
    if request.method == 'GET':
        form = PrettyModelFrom()
        return render(request, 'pretty_add.html', {"form": form})
    form = PrettyModelFrom(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/pretty/list')
    return render(request, 'pretty_add.html', {'form': form})


def pretty_edit(request, nid):
    '''编辑靓号'''
    row_data = models.PrettyNum.objects.filter(id=nid).first()
    if request.method == 'GET':
        form = PrettyEditModelFrom(instance=row_data)
        return render(request, 'pretty_edit.html', {'form': form})
    form = PrettyEditModelFrom(data=request.POST, instance=row_data)
    if form.is_valid():
        form.save()
        return redirect('/pretty/list')
    return render(request, 'pretty_edit.html', {'form': form})


def pretty_delete(request, nid):
    '''靓号删除'''
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect('/pretty/list')


class AdminModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.Admin
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            "password": forms.PasswordInput(render_value=True)
            # render_valuer=True 保留密码的值
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        md5_pwd = md5(pwd)

        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if md5(confirm_password) != pwd:
            raise ValidationError('密码不一致')
        return confirm_password


class AdminEditModelForm(BootStrapModelForm):
    class Meta:
        model = models.Admin
        fields = ['username']


class AdminResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.Admin
        fields = ['password', 'confirm_password']
        widgets = {
            "password": forms.PasswordInput(render_value=True)
            # render_valuer=True 保留密码的值
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        md5_pwd = md5(pwd)
        exist = models.Admin.objects.filter(id=self.instance.pk, password=md5_pwd).exists()
        if exist:
            raise ValidationError('密码不能与原密码一直')
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if md5(confirm_password) != pwd:
            raise ValidationError('密码不一致')
        return confirm_password


def admin_list(request):
    '''管理员列表'''
    search_data = request.GET.get("q", "")
    data = {}
    if search_data:
        data['username__contains'] = search_data
    queryset = models.Admin.objects.filter(**data)
    return render(request, 'admin_list.html', {"queryset": queryset, "search_data": search_data})


def admin_add(request):
    '''管理员添加'''
    title = '管理员添加'
    if request == 'GET':
        form = AdminModelForm()
        context = {
            "title": title,
            "form": form
        }
        return render(request, 'change.html', context)
    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/admin/list')
    context = {
        "title": title,
        "form": form
    }
    return render(request, 'change.html', context)


def admin_edit(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect('/admin/list')
    if request.method == 'GET':
        form = AdminEditModelForm(instance=row_object)
        context = {
            "title": '编辑管理员',
            "form": form
        }
        return render(request, 'change.html', context)

    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list")
    context = {
        "title": '编辑管理员',
        "form": form
    }
    return render(request, 'change.html', context)


def admin_delete(request, nid):
    models.Admin.objects.filter(id=nid).delete()
    return redirect("/admin/list")


def admin_reset(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect('/admin/list')
    title = "重置密码--{}".format(row_object.username)
    if request.method == 'GET':
        form = AdminResetModelForm()
        return render(request, 'change.html', {"title": title, "form": form})
    form = AdminResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect("/admin/list")
    return render(request, 'change.html', {"title": title, "form": form})


# required=True表示必填
class LoginForm(BootStrapForm):
    username = forms.CharField(label='用户名', widget=forms.TextInput(attrs={'name': 'username'}), required=True)
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True, attrs={'name': 'password'}),
                               required=True)
    code = forms.CharField(label='验证码', widget=forms.TextInput, required=True)

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return md5(pwd)


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
    form = LoginForm(data=request.POST)
    if form.is_valid():
        '''进行校验'''
        # 验证码的校验
        user_input_code = form.cleaned_data['code']
        code = request.session.get('image_code', '')
        if code.upper() != user_input_code.upper():
            form.add_error("code", '验证码错误')
            return render(request, 'login.html', {"form": form})
        admin_object = models.Admin.objects.filter(username=form.cleaned_data['username'],
                                                   password=form.cleaned_data['password']).first()
        print(form.cleaned_data['username'],form.cleaned_data['password'])
        if not admin_object:
            # 用户名密码错误
            form.add_error("password", "用户名或密码错误")
            return render(request, 'login.html', {"form": form})
        # 用户名密码正确
        # 网站生成随机字符串，写到用户浏览器的cookie中，然后写入到session中
        request.session['info'] = {"id": admin_object.id, "name": admin_object.username}
        # 重新设置过期时间 用户信息保存7天
        request.session.set_expiry(60 * 60 * 24 * 7)
        return redirect("/admin/list")
    return render(request, 'login.html', {"form": form})


def image_code(request):
    '''生成图片验证码'''
    img, code_string = check_code()
    stream = BytesIO()
    img.save(stream, 'png')
    # 写入到session中，便于后面校验
    request.session['image_code'] = code_string
    # 设置60秒超时
    request.session.set_expiry(60)
    return HttpResponse(stream.getvalue())


class TaskModelForm(BootStrapModelForm):
    class Meta:
        model = models.Task
        fields = "__all__"
        widgets = {
            "detail": forms.TextInput
        }


def logout(request):
    request.session.clear()
    return redirect('/login/')


def task_list(request):
    form = TaskModelForm()
    return render(request, 'task_list.html', {"form": form})


@csrf_exempt
def task_ajax(request):
    print(request.POST)
    data_dict = {"status": True, "data": [11, 22, 33, 44]}
    return HttpResponse(json.dumps(data_dict))
    # return JsonResponse(data_dict)


@csrf_exempt
def task_add(request):
    print(request.POST)
    form = TaskModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        data_dict = {"status": True}
        return HttpResponse(json.dumps(data_dict))
    data_dict = {"status": False, "error": form.errors}
    return HttpResponse(json.dumps(data_dict))


class OrderModelForm(BootStrapModelForm):
    class Meta:
        model = models.Order
        exclude = ['oid', "admin"]


def order_list(request):
    page = int(request.GET.get('page', '1'))
    page_size = 10
    start = (page - 1) * page_size
    end = page * page_size

    total_count = models.Order.objects.all().order_by('-id').count()
    queryset = models.Order.objects.all().order_by('id')[start:end]
    total_page_count, div = divmod(total_count, page_size)
    if div:
        total_page_count += 1

    # 根据计算，显示前五页后五页
    plus = 5
    if total_page_count < plus * 2 + 1:
        # 数据库数据比较少 ，只显示11页
        start_page = 1
        end_page = plus * 2 + 1
    else:
        # 小的极值  小于5页
        if page < plus:
            start_page = 1
            end_page = plus * 2 + 1
        else:
            # 当前页面加5超过最大页数了
            if page + plus > total_page_count:
                start_page = total_page_count - plus * 2
                end_page = total_page_count + 1
            else:
                start_page = page - plus
                end_page = page + plus + 1
    # 页码
    page_str_list = []
    # 首页
    page_str_list.append('<li><a href="?page=1">首页</a></li>')
    # 上一页
    if page > 1:
        prev = f'<li><a href="?page={page - 1}">上一页</a></li>'
    else:
        prev = '<li><a href="?page=1">上一页</a></li>'
    page_str_list.append(prev)

    # 页面
    for i in range(start_page, end_page):
        if i == page:
            ele = f'<li class="active"><a href="?page={i}">{i}</a></li>'
        else:
            ele = f'<li ><a href="?page={i}">{i}</a></li>'
        page_str_list.append(ele)

        # 上一页
    if page < total_page_count:
        prev = f'<li><a href="?page={page + 1}">下一页</a></li>'
    else:
        prev = f'<li><a href="?page={total_page_count}">下一页</a></li>'
    page_str_list.append(prev)
    # 尾页
    page_str_list.append(f'<li><a href="?page={total_page_count}">首页</a></li>')

    page_string = mark_safe("".join(page_str_list))
    form = OrderModelForm()
    return render(request, 'order_list.html',
                  {'queryset': queryset, "page_string": page_string, "form": form})


def gettime():
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))


@csrf_exempt
def order_add(request):
    """新建订单"""

    form = OrderModelForm(data=request.POST)
    if form.is_valid():
        # 固定设置管理员id为当前登录用户的id
        form.instance.admin_id = request.session['info']['id']
        form.instance.oid = gettime()
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def order_delete(request):
    '''删除订单'''
    uid = request.GET.get('uid')
    exists = models.Order.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status": False, "error": '数据不存在'})

    models.Order.objects.filter(id=uid).delete()
    return JsonResponse({"status": True, "error": '删除成功'})


def order_detail(request):
    ''' 根据ID获取订单详细'''
    # 方法一
    # uid=request.GET.get('uid')
    # row_object=models.Order.objects.filter(id=uid).first()
    # if not row_object:
    #     return JsonResponse({"status":False,"error":'数据不存在'})
    #
    # result={
    #     "status":True,
    #     "data":{
    #         "title":row_object.title,
    #         "price":row_object.price,
    #         "status":row_object.status,
    #     }
    # }
    # return JsonResponse({"status":True,"data":result})
    # 方法二
    uid = request.GET.get('uid')
    row_object = models.Order.objects.filter(id=uid).values('title', 'price', 'status').first()
    if not row_object:
        return JsonResponse({"status": False, "error": '数据不存在'})
    result = {
        "status": True,
        "data": row_object,
    }
    return JsonResponse(result)


@csrf_exempt
def order_edit(request):
    '''编辑'''
    uid = request.GET.get('uid')
    print(uid)
    row_object = models.Order.objects.filter(id=uid).first()

    if not row_object:
        return JsonResponse({"status": False, "tips": "数据不存在"})

    form = OrderModelForm(data=request.GET, instance=row_object)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def chart_list(request):
    '''数据统计页面'''
    return render(request, 'chart_list.html')


def chart_bar(request):
    '''构造柱状图数据'''
    # 数据可以去数据库获取

    legend = ['周星驰', '桂佳磊']
    series_list = [
        {
            'name': '周星驰',
            'type': 'bar',
            'data': [5, 20, 36, 10, 10, 20]
        },
        {
            'name': '桂佳磊',
            'type': 'bar',
            'data': [45, 15, 6, 8, 5, 25]
        }]
    x_axis = ['1月', '2月', '3月', '4月', '5月', '6月']
    result = {
        "status": True,
        "data": {
            "legend": legend,
            "series_list": series_list,
            "x_axis": x_axis,
        }
    }
    return JsonResponse(result)


def chart_pie(request):
    '''构造饼图数据'''
    data = [
        {'value': 1048, 'name': 'IT'},
        {'value': 735, 'name': '运营'},
        {'value': 580, 'name': '自媒体'},
        {'value': 2410, 'name': '开发部'},
    ]
    result = {
        "status": True,
        "data": data
    }
    return JsonResponse(result)


def chart_line(request):
    legend = ['上海', '北京', '深圳', '杭州', '南京']
    series = [{
        'name': '上海',
        'type': 'line',
        'stack': 'Total',
        'data': [120, 132, 101, 134, 90, 230, 210]
    },
        {
            'name': '北京',
            'type': 'line',
            'stack': 'Total',
            'data': [220, 182, 191, 234, 290, 330, 310]
        },
        {
            'name': '深圳',
            'type': 'line',
            'stack': 'Total',
            'data': [150, 232, 201, 154, 190, 330, 410]
        },
        {
            'name': '杭州',
            'type': 'line',
            'stack': 'Total',
            'data': [320, 332, 301, 334, 390, 330, 320]
        },
        {
            'name': '南京',
            'type': 'line',
            'stack': 'Total',
            'data': [820, 932, 901, 934, 1290, 1330, 1320]
        }]

    x_axis = ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    result = {
        "status": True,
        "data": {
            'legend': legend,
            "series": series,
            "x_axis": x_axis,
        }
    }
    return JsonResponse(result)





def file(request):
    if request.method=='GET':
        return render(request,'file.html')
    file_object=request.FILES.get('file_up')
    print(file_object.name)
    f=open(f"staffsystem/media/avatars/{file_object.name}",mode='wb')
    for chunk in file_object.chunks():
        f.write(chunk)
    f.close()
    return HttpResponse('...')