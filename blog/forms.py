# -*- coding:utf-8 -*-

from django.forms import Form,fields,widgets
from django.core.exceptions import ValidationError
import time
from blog import models

class RegisterForm(Form):
    username = fields.CharField(widget=widgets.TextInput(attrs={"class":"form-control"}))
    email = fields.EmailField(widget=widgets.TextInput(attrs={"class":"form-control"}))
    password = fields.CharField(widget=widgets.TextInput(attrs={"class":"form-control","type":"password"}))
    password2 = fields.CharField(widget=widgets.TextInput(attrs={"class":"form-control","type":"password"}))
    avatar = fields.FileField(widget=widgets.FileInput(attrs={"class":"f1","id":"imgSelect"}))
    code = fields.CharField(widget=widgets.TextInput(attrs={"class":"form-control"}))
    nickname = fields.CharField(required=False,widget=widgets.TextInput(attrs={"class":"form-control"}))
    create_time = fields.DateTimeField(required=False)


    # 传入request是为了检查session中的code字段
    def __init__(self,request,*args,**kwargs):  # 传入request
        super(RegisterForm, self).__init__(*args,**kwargs)
        self.request = request


    def clean_code(self):
        input_code = self.cleaned_data["code"]
        session_code = self.request.session.get("code")
        if input_code.upper() != session_code.upper():
            raise ValidationError("验证码错误")
        return input_code

    # 检出用户名是否已被占用
    def clean_username(self):
        username = self.cleaned_data["username"]
        if models.UserInfo.objects.filter(username=username):
            raise ValidationError("该用户已被占用")
        return username

    # 检出邮箱是否已被占用
    def clean_email(self):
        email = self.cleaned_data["email"]
        if models.UserInfo.objects.filter(email=email):
            raise ValidationError("该邮箱已被占用")
        return email

    # 检出nickname是否已被占用
    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"]
        if models.UserInfo.objects.filter(nickname=nickname):
            raise ValidationError("该昵称已被占用")
        return nickname

    def clean(self):
        # 检查两次密码是否一致
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 != p2:
            self.add_error("password2", ValidationError("密码不一致"))
            # raise ValidationError("密码不一致")
        else:
            self.cleaned_data.pop("password2",None)  # 如果一致，则去除password2，只保留password，为了与数据库字段一致（数据库只有password）
            # return self.cleaned_data
            # return None # 两者均可

        # 如无创建时间，添加创建时间
        # if not self.cleaned_data.get("create_time"):
        #     self.cleaned_data["create_time"] = time.strftime("%Y-%m-%d")
        # 如无nickname，添加nickname
        if not self.cleaned_data.get("nickname"):
            self.cleaned_data["nickname"] = self.cleaned_data.get("username","")+str(int(time.time()))
        # 如果验证码正确，去除code，目的是与数据库字段一致（数据库没code）
        if self.cleaned_data.get("code"):
            self.cleaned_data.pop("code")
        return self.cleaned_data


class ArticleForm(Form):
    title = fields.CharField(max_length=64)
    content = fields.CharField(
        widget=widgets.Textarea(attrs={"id":"i1"})
    )

    def clean_content(self):
        old = self.cleaned_data["content"]
        from utils.xss import xss

        return xss(old)
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(old,"html.parser")
        # valid_tag = {
        #     "p":["class","id"],
        #     "img":["src"],
        #     "div":["class"],
        # }
        # tags = soup.find_all()
        # for tag in tags:
        #     if tag.name not in valid_tag:
        #         tag.decompose()  # 删除整个标签
        #         # tag.clear()  # 删除标签里的内容
        #     if tag.attrs:  # 有些是空字典
        #         for k in list(tag.attrs.keys()):  # {"id":"i1","a"=123,"b"=999}
        #             if k not in valid_tag[tag.name]:
        #                 del tag.attrs[k]  # 删除属性
        #
        # content_str = soup.decode()
        # return content_str