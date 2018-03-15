"""qiuzhiquan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, re_path, include
from django.views.static import serve

from interview.views import InterListView, InterDetailView, RegView, LoginView, LogoutView, IndexView, AddCommentView, \
    ContactView, FaqView
from qiuzhiquan.settings import MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls),
    path('interlist/', InterListView.as_view(), name="interlist"),  # 名企面经映射
    path('ueditor/', include('DjangoUeditor.urls')),  # 增加ueditor映射
    path('register/', RegView.as_view(), name="register"),  # 用户注册页映射
    path('login/', LoginView.as_view(), name="login"),  # 用户登录页映射
    path('logout/', LogoutView.as_view(), name="logout"),  # 用户注销映射
    path('', IndexView.as_view(), name="index"),  # 首页映射
    path('contact/', ContactView.as_view(), name="contact"),  # 联系页映射
    path('faq/', FaqView.as_view(), name="faq"),  # 常见问题页映射
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),  # 管理媒体文件路径和处理模块
    re_path(r'^interdetail/(?P<interview_id>\d+)/$', InterDetailView.as_view(), name='interdetail'),  # 面经详情页映射
    re_path(r'^addcomment/(?P<interview_id>\d+)/$', AddCommentView.as_view(), name='addcomment'),  # 用户评论映射
]

# 404和500配置
handler404 = 'interview.views.view_404'
handler500 = 'interview.views.view_500'
