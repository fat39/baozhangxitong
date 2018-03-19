from utils.pager import PageInfo
from django.shortcuts import render,HttpResponse,redirect
from django.views import View
from blog import forms
import time
from blog import models

# Create your views here.

def codecheck(request):
    from io import BytesIO  # 在内存中开辟一块空间
    from utils.random_check_code import rd_check_code
    img,code = rd_check_code()
    stream = BytesIO()
    img.save(stream,"png")  # 图片以png的格式存储到内存stream中
    request.session["code"] = code  # 验证码存储在session中
    print(request.session.get("code"))
    return HttpResponse(stream.getvalue())

def upload_avatar(request):
    if request.method == "POST":
        import os
        import time
        # print(request.POST, request.FILES)
        file_obj = request.FILES.get("my_avatar")
        # file_path = os.path.join("static","imgs", file_obj.name)
        file_path = os.path.join("static","imgs","avatar",str(time.time()))
        with open(file_path, "wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        return HttpResponse(file_path)

class Login(View):
    def get(self,request,*args,**kwargs):
        return render(request,"blog/login.html")

    def post(self,request,*args,**kwargs):
        input_code = request.POST.get("code")
        session_code = request.session.get("code")
        if input_code.upper() == session_code.upper():
            # 验证码正确
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = models.UserInfo.objects.filter(username=username, password=password)
            if user:
                # 用户名密码正确
                request.session["userinfo"] = {
                    "username": username,
                }
                return redirect("/")
            else:
                # 用户名密码错误
                return render(request, "blog/login.html", {"err_login": "用户名或密码错误"})
        else:
            # 验证码错误
            return render(request, "blog/login.html", {"err_code": "验证码错误"})

def logout(request):
    del request.session["userinfo"]
    request.session.delete("session_key")
    return redirect("/")


class Register(View):
    def get(self,request,*args,**kwargs):
        new_user = forms.RegisterForm(request)
        return render(request,"blog/register.html",{"new_user":new_user})
    def post(self,request,*args,**kwargs):
        # 验证码操作
        new_user = forms.RegisterForm(request,request.POST,request.FILES)
        if new_user.is_valid():
            # 写入头像返回路径
            avatar_path = "static/imgs/avatar/{}".format(new_user.cleaned_data["nickname"],)
            with open(avatar_path,"wb") as f:
                for chunk in new_user.files["avatar"].chunks():
                    f.write(chunk)

            new_user.cleaned_data["avatar"] = avatar_path
            models.UserInfo.objects.create(**new_user.cleaned_data)
            return redirect("/login.html")
        else:
            return render(request,"blog/register.html",{"new_user":new_user})
            # obj.errors
            # clean方法出错了，err放在__all__

class Index(View):
    def get(self, request, *args, **kwargs):
        # 获取当前URL
        # print(request.path_info)

        condition = {}
        type_id = int(kwargs.get("type_id")) if kwargs.get("type_id") else None
        if type_id:
            condition['article_type_id'] = type_id

        # article_list = models.Article.objects.filter(**condition)

        type_choice_list = models.Article.type_choices


        # 分页
        target_Article_objs = models.Article.objects.filter(**condition)
        all_count = target_Article_objs.count()
        # all_count = models.Article.objects.filter(**condition).count()  # 查询符合条件的条目数量
        page_info = PageInfo(request.GET.get("page"), all_count, 5, "", 11)
        # article_list = models.Article.objects.filter(**condition)[page_info.start():page_info.end()]
        article_list = target_Article_objs[page_info.start():page_info.end()]
        # print(article_list[0].blog.user.avatar)
        # 取多少个值，可能存在少于10个的情况
        TOP10_amount = 10 if all_count>=10 else all_count
        most_up_count = target_Article_objs.order_by("-up_count")[:TOP10_amount]
        most_comment_count = target_Article_objs.order_by("-comment_count")[:TOP10_amount]
        print(models.Article.objects.values())
        return render(
            request,
            "blog/index.html",
            {
                "type_choice_list":type_choice_list,
                "article_list":article_list,
                "type_id":type_id,
                "page_info":page_info,
                "most_up_count":most_up_count,
                "most_comment_count":most_comment_count,
             }
        )


