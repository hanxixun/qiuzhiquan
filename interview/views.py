from django.contrib.auth import authenticate, login, logout  # 导入用户登录/登出/认证
from django.contrib.auth.hashers import make_password  # 导入密码加密模块
from django.db.models import Q  # 导入或判断模块
from django.http import HttpResponseRedirect, HttpResponse  # 导入重定向模块
from django.shortcuts import render, redirect, render_to_response
from django.urls import reverse  # 导入reverse解析模块（用来做重定向）
from django.views import View
from interview.forms import RegForm, LoginFrom, CommentForm  # 导入用户表单（注册/登录/评论）
from interview.models import Interview, Author, User, Comment, Faq
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger  # 导入分页库的类


# Create your views here.
class InterListView(View):
    """
    名企面经列表类
    """

    def get(self, request):
        # 取出所有面经
        all_interviews = Interview.objects.all()  # 获取所有的面经对象（列表）

        # 点击搜索
        keywords = request.GET.get('keywords', "")
        if keywords:
            all_interviews = Interview.objects.filter(
                Q(title__icontains=keywords) | Q(desc__icontains=keywords) | Q(content__icontains=keywords))
        # 基于公司分类
        company = request.GET.get('company', "")
        if company:
            all_interviews = Interview.objects.filter(company=company)

        # 基于行业分类
        trade = request.GET.get('trade', "")
        if trade:
            all_interviews = Interview.objects.filter(trade=trade)

        # 基于年级分类(基于年级找作者，基于作者找面经)
        year = request.GET.get('year', "")  # 获取关键字year,若没有则设置为空
        if year:
            authors = Author.objects.filter(year=year)  # 取出这个年级对应的作者
            all_interviews = Interview.objects.none()  # 设置空面经queryset

            for author in authors:
                interviews = author.interview_set.all()  # 获取每个作者对应的面经（author和interview存在一对多的外键关系，可以调用interview_set方法）
                all_interviews = all_interviews | interviews  # 讲每个作者的面经合并起来(queryset)

        # 对面经列表分页
        try:
            page = request.GET.get('page', 1)
        except(PageNotAnInteger, EmptyPage):
            page = 1
        p = Paginator(all_interviews, 2, request=request)
        interviews = p.page(page)
        return render(request, "interview_list.html", {
            "all_interviews": interviews,  # 传递模板变量给模板文件
        })


class InterDetailView(View):
    '''
    面经详情页
    '''

    def get(self, request, interview_id):
        interview = Interview.objects.get(id=int(interview_id))  # 传入interview_id参数（此参数通过url映射得到)

        # 增加阅读次数
        interview.read_counts += 1
        interview.save()

        # 推荐面经(同公司)
        recommended_tag = interview.company  # company_tag
        recommended_interviews = Interview.objects.filter(company=recommended_tag).exclude(
            id=int(interview_id)).order_by('-read_counts')[:3]

        # 推荐面经(同行业)
        recommended_tag2 = interview.trade  # trade_tag
        recommended_interviews2 = Interview.objects.filter(trade=recommended_tag2).exclude(
            company=recommended_tag).order_by('-read_counts')[:3]

        # 评论显示
        comments = Comment.objects.filter(interview=interview).order_by("-pub_time")

        return render(request, "interview_detail.html", {
            "interview": interview,
            "recommended_interviews": recommended_interviews,
            "recommended_interviews2": recommended_interviews2,
            "comments": comments,
        })


class RegView(View):
    """
    用户注册类
    """

    def get(self, request):
        return render(request, "reg.html", {})

    def post(self, request):
        regform = RegForm(request.POST)
        if regform.is_valid():
            username = request.POST.get("email", "")
            email = request.POST.get("email", "")
            password = request.POST.get("password", "")
            user = User()
            user.username = username
            user.email = email
            user.password = password
            user.password = make_password(password)
            user.save()
            return render(request, "login.html", {})
        else:
            return render(request, "reg.html", {
                "regform": regform
            })


class LoginView(View):
    """
    用户登录类
    """

    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        loginform = LoginFrom(request.POST)
        if loginform.is_valid():
            username = request.POST.get("email", "")
            password = request.POST.get("password", "")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            else:
                return render(request, "login.html", {
                    "error": '登录验证失败'
                })
            return HttpResponseRedirect(reverse("index"))  # 重定向到首页
        return render(request, "login.html", {
            "error": '登录验证失败'
        })


class LogoutView(View):
    """
    用户注销
    """

    def get(self, request):
        logout(request)  # 退出
        return HttpResponseRedirect(reverse("index"))  # 重定向到首页


class IndexView(View):
    """
    首页
    """

    def get(self, request):
        all_interviews = Interview.objects.all().order_by('-read_counts')[:6]
        return render(request, "index.html", {
            "all_interviews": all_interviews,
        })


class AddCommentView(View):
    """
    添加评论
    """

    def post(self, request, interview_id):
        interview = Interview.objects.get(id=int(interview_id))
        if request.user.is_authenticated:  # 判断用户是否登录
            comment_form = CommentForm(request.POST)  # 创建表单实例
            if comment_form.is_valid():  # 判断表单输入是否有效
                content = request.POST.get('comment')  # 若有效则获取内容
                comments = Comment()  # 创建评论实例
                comments.comment = content  # 为评论字段赋值
                comments.user = request.user  # 评论用户
                comments.interview = interview  # 被评论面经
                comments.save()
                return redirect(request.META['HTTP_REFERER'])  # 若表单内容已经保存，则刷新本页面
            else:
                return HttpResponse("请输入正确的评论内容")  # 若表单信息无效，给用户错误警告
        else:  # 如果登录失败或者用户未登录，则重定向/返回到登录页面
            return render(request, "login.html", {
                "error": "请登录后再评论"
            })


class ContactView(View):
    """
    联系页
    """

    def get(self, requeset):
        return render(requeset, "contact.html", {})


class FaqView(View):
    """
    常见问答
    """

    def get(self, request):
        all_faqs = Faq.objects.all()[:5]  # 获取所有回答
        return render(request, "faq.html", {
            "all_faqs": all_faqs
        })


# http状态码:200 404 500 302
def view_404(request):
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response

def view_500(request):
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response