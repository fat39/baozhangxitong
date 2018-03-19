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
from django.contrib import admin
from django.urls import path,re_path
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path("^$",views.Index.as_view()),
    re_path(r'^all/(?P<type_id>\d+)/$',views.Index.as_view()),
    re_path("^codecheck/$",views.codecheck),
    re_path("^login.html$",views.Login.as_view()),
    re_path("^register.html$",views.Register.as_view()),
    re_path("^logout/$",views.logout),
    re_path(r'^uploadAvatar/$', views.upload_avatar),
]
