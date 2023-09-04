"""
URL configuration for staffsystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from staff import views
urlpatterns = [
    # 部门管理
    path('depart/list',views.depart_list ),
    path('depart/add',views.depart_add ),
    path('depart/delete',views.depart_delete),
    path('depart/<int:nid>/edit',views.depart_edit),
    #用户管理
    path('user/list',views.user_list),
    path('user/add',views.user_add),
    path('user/<int:nid>/edit',views.user_edit),
    path('user/<int:nid>/delete',views.user_delete),
    #靓号管理
    path('pretty/list',views.pretty_list),
    path('pretty/add',views.pretty_add),
    path('pretty/add',views.pretty_add),
    path('pretty/<int:nid>/edit',views.pretty_edit),
    path('pretty/<int:nid>/delete',views.pretty_delete),
    # 管理员管理
    path('admin/list',views.admin_list),
    path('admin/add',views.admin_add),
    path('admin/<int:nid>/edit',views.admin_edit),
    path('admin/<int:nid>/delete',views.admin_delete),
    path('admin/<int:nid>/reset',views.admin_reset),
    # 登录 注销
    path('login/',views.login),
    path('logout/',views.logout),
    path('image/code',views.image_code),
    # 任务管理

    path('task/list/',views.task_list),
    path('task/ajax/',views.task_ajax),
    path('task/add/',views.task_add),
    #订单管理
    path('order/list/',views.order_list),
    path('order/add/',views.order_add),
    path('order/delete/',views.order_delete),
    path('order/detail/',views.order_detail),
    path('order/edit/',views.order_edit),

    # 数据统计
    path('chart/list/',views.chart_list),
    path('chart/bar/',views.chart_bar),
    path('chart/pie/',views.chart_pie),
    path('chart/line/',views.chart_line),
    # 文件上传
    path('file/',views.file),
]
