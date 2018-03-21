import json
from django.db.models import F
from django.conf import settings
from django.db.models import Count, Min, Max, Sum
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
            user = models.UserInfo.objects.filter(username=username, password=password).first()
            site = user.blog.site
            if user:
                # 用户名密码正确
                request.session["userinfo"] = {
                    "user_id":user.nid,
                    "username": username,
                    "site":site,
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
        target_Article_objs = models.Article.objects.filter(**condition).order_by("-create_time")
        all_count = target_Article_objs.count()
        # all_count = models.Article.objects.filter(**condition).count()  # 查询符合条件的条目数量
        page_info = PageInfo(request.GET.get("page"), all_count, settings.ITEMS_PER_PAGE, "", )
        # article_list = models.Article.objects.filter(**condition)[page_info.start():page_info.end()]
        article_list = target_Article_objs[page_info.start():page_info.end()]
        # print(article_list[0].blog.user.avatar)
        # 取多少个值，可能存在少于10个的情况
        TOP10_amount = 10 if all_count>=10 else all_count
        most_up_count = target_Article_objs.order_by("-up_count")[:TOP10_amount]
        most_comment_count = target_Article_objs.order_by("-comment_count")[:TOP10_amount]
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


def getlayout(blog):
    fans_objs = models.UserFans.objects.filter(user=blog.user)
    myfollow_objs = models.UserFans.objects.filter(follower=blog.user)
    tag_list = models.Article.objects.filter(blog=blog).values("tags__title", "tags__nid").annotate(ct=Count("nid"))
    category_list = models.Article.objects.filter(blog=blog).values("category__title", "category__nid").annotate(
        ct=Count("nid"))
    date_list = models.Article.objects.filter(blog=blog).extra(
        select={"Year_month": 'strftime("%%Y-%%m",create_time)'}).values("Year_month").annotate(ct=Count("nid"))
    pageinfo = {
        "blog":blog,
        "fans_objs": fans_objs,
        "myfollow_objs": myfollow_objs,
        "tag_list": tag_list,
        "category_list": category_list,
        "date_list": date_list,
    }
    return pageinfo


class HomePage(View):
    def get(self,request,**kwargs):
        site = kwargs.get("site")
        blog = models.Blog.objects.filter(site=site).first()
        if blog:
            sort = kwargs.get("sort")
            sort_val = kwargs.get("sort_val")
            if sort == "tag":  # 按标签
                article_list = models.Article.objects.filter(blog=blog, tags__nid=sort_val)
            elif sort == "category":  # 按分类
                article_list = models.Article.objects.filter(blog=blog, category__nid=sort_val)
            elif sort == "date":
                article_list = models.Article.objects.filter(blog=blog).extra(
                    select={"Year_month": 'strftime("%%Y-%%m",create_time)'}).extra(where=["Year_month=%s"],
                                                                                    params=[sort_val])
            else:  # 所有文章
                article_list = models.Article.objects.filter(blog=blog)
            """
                缺 year_month
            """

            # fans_objs = models.UserFans.objects.filter(user=blog.user)
            # myfollow_objs = models.UserFans.objects.filter(follower=blog.user)
            # tag_list = models.Article.objects.filter(blog=blog).values("tags__title","tags__nid").annotate(ct=Count("nid"))
            # category_list = models.Article.objects.filter(blog=blog).values("category__title","category__nid").annotate(ct=Count("nid"))
            # date_list = models.Article.objects.filter(blog=blog).extra(select={"Year_month":'strftime("%%Y-%%m",create_time)'}).values("Year_month").annotate(ct=Count("nid"))
            pageinfo = getlayout(blog)

            page_info = PageInfo(request.GET.get("page"), len(article_list), settings.ITEMS_PER_PAGE, "", )
            # pageinfo["article_list"] = article_list.order_by("-create_time")
            pageinfo["article_list"] = article_list.order_by("-create_time")[page_info.start():page_info.end()]
            pageinfo["page_info"] = page_info


            # pageinfo = {
            #     "blog": blog,
            #     "article_list": article_list.order_by("-create_time"),
            #     "fans_objs":fans_objs,
            #     "myfollow_objs":myfollow_objs,
            #     "tag_list":tag_list,
            #     "category_list":category_list,
            #     "date_list": date_list,
            # }

            return render(request, "blog/homepage.html", pageinfo)
        else:
            return redirect("/")


class Article(View):
    def get(self,request,**kwargs):
        site = kwargs.get("site")
        blog = models.Blog.objects.filter(site=site).first()
        pageinfo = getlayout(blog)

        article_id = kwargs.get("article_id")
        this_article = models.Article.objects.filter(nid=article_id).first()

        pageinfo["this_article"] = this_article
        return render(request,"blog/article_detail.html",pageinfo)


def comments(request,nid):
    import json
    response = {"status":True,"data":None,"msg":None}
    try:
        comments = models.Comment.objects.filter(article_id=nid).values(
            "nid","content","create_time","reply_id","article_id","user__nickname","user__blog__site","user_id"
        )
        # comments = models.Comment.objects.filter(article_id=nid).values()
        # for item in comments:
        #     print(item)
        comments_dict = {}
        comments_list = []
        for item in comments:
            comments_dict[item["nid"]] = item
            item.setdefault("child", [])
            reply_id = item.get("reply_id")
            if reply_id:
                comments_dict[reply_id]["child"].append(item)
            else:
                comments_list.append(item)
        response["data"] = comments_list
    except Exception as e:
        response["status"] = False
        response["msg"] = str(e)

    print(response)
    return HttpResponse(json.dumps(response))


def up(request):
    userinfo = request.session.get("userinfo")
    art_id = request.POST.get("art_id")
    # val = int(request.POST.get("val"))
    response = {"status":True,"msg":None}
    if userinfo:
        user_id = userinfo["user_id"]
        up = models.UpDown.objects.filter(article_id=art_id,user_id=user_id)
        if up:
            # 已经赞过
            response["status"] = False
            pass
        else:
            from django.db import transaction
            with transaction.atomic():  # 出错了会报异常，但不会提交
                # up_count = models.Article.objects.filter(nid=art_id).first().up_count
                models.UpDown.objects.create(article_id=art_id,user_id=user_id,up=True)
                models.Article.objects.filter(nid=art_id).update(up_count=F("up_count")+1)
                up_count = models.Article.objects.filter(nid=art_id).first().up_count
                response["up_count"] = up_count
    else:
        response["status"] = False
    return HttpResponse(json.dumps(response))


class Backend(View):
    def get(self,request,*args,**kwargs):
        return render(request,"blog/backend.html")


