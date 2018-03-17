from django.shortcuts import render,HttpResponse,redirect
from django.views import View
from blog import forms

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

class Login(View):
    def get(self,request,*args,**kwargs):
        return render(request,"blog/login.html")

class Register(View):
    def get(self,request,*args,**kwargs):
        newuser = forms.RegisterForm(request)
        return render(request,"blog/register.html",{"newuser":newuser})