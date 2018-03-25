"""baozhangxitong URL Configuration

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
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from django.urls import path,re_path
from blog import views


urlpatterns = [

    path('admin/', admin.site.urls),
    # 登录注册
    re_path("^login.html$", views.Login.as_view()),
    re_path("^register.html$", views.Register.as_view()),
    re_path("^logout/$", views.logout),

    # 主页
    # re_path("^$",views.test),
    re_path("^$",views.Index.as_view()),
    re_path(r'^all/(?P<type_id>\d+)/$',views.Index.as_view()),
    re_path("^codecheck/$",views.codecheck),

    # 某项功能
    re_path(r'^uploadAvatar/$', views.upload_avatar),
    re_path(r"^updown/$",views.up),

    # 后台
    re_path(r"^backend/$", views.Backend.as_view()),
    # re_path(r"^backend/article.html$",csrf_exempt(views.BackendArticleManage.as_view())),
    re_path(r"^backend/article.html$",views.BackendArticleManage.as_view()),
    re_path(r"^backend/article-(?P<article_type_id>\d*)-(?P<category_id>\d*)-(?P<tags__nid>\d*).html$",views.BackendArticleManage.as_view()),
    re_path(r"^backend/article_(create|modify)/$",views.BackendArticle.as_view()),
    re_path(r"^backend/articeldel/$",views.BackendArticleDelete.as_view()),


    # 个人博客
    re_path(r'^(?P<site>\w+)/$', views.HomePage.as_view()),
    re_path(r'^(?P<site>\w+)/(?P<sort>tag|category|date)+/(?P<sort_val>[^/]+)/*$', views.HomePage.as_view()),
    re_path(r'^(?P<site>\w+)/(?P<article_id>\d+).html$', views.Article.as_view()),
    re_path(r'^comments-(?P<article_id>\d+).html$', views.Comments.as_view()),

]
