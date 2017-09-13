from datetime import datetime

from django.shortcuts import render, reverse, redirect
# from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth import authenticate, login, logout
# from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Category, Page, UserProfile
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm


'''将信息储存在客户端的cookie中'''
# def vistor_cookie_handler(request, response):
#     visits = int(request.COOKIES.get('visits', '1'))
#
#     last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
#     last_visit_time = datetime.strptime(last_visit_cookie[:-7],
#                                         '%Y-%m-%d %H:%M:%S')
#
#     if (datetime.now() - last_visit_time).seconds > 0:
#         visits += 1
#         response.set_cookie('last_visit', str(datetime.now()))
#     else:
#         response.set_cookie('last_visit', last_visit_cookie)
#
#     response.set_cookie('visits', visits)


def get_server_side_cookie(request, cookie, default_val=None):
    """将信息储存在服务端的session中"""
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def index(request):
    # request.session.set_test_cookie()
    context = {}
    context['categories'] = Category.objects.order_by('-likes')[:5]
    context['pages'] = Page.objects.order_by('-views')[:5]
    visitor_cookie_handler(request)
    context['visits'] = request.session.get('visits')

    return render(request, 'rango/index.html', context=context)


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    else:
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['category'] = category
        context_dict['pages'] = pages

    return render(request, 'rango/category.html', context=context_dict)


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', context={'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_list = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context=context_list)


# def register(request):
#     user_form = UserForm()
#     profile_form = UserProfileForm()
#     registered = False
#
#     if request.method == 'POST':
#         user_form = UserForm(request.POST)
#         profile_form = UserProfileForm(request.POST)
#
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()
#
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#             profile.save()
#
#             registered = True
#         else:
#             print(user_form.errors, profile_form.errors)
#
#     return render(request, 'rango/register.html', {'user_form': user_form,
#                                                    'profile_form': profile_form,
#                                                    'registered': registered})


# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(username=username, password=password)
#
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('rango:index'))
#             else:
#                 return render(request, 'rango/login.html',
#                               {'error_msg': 'Your rango account is disabled.'})
#         else:
#             print('Invalid login details: {}, {}'.format(username, password))
#             return render(request, 'rango/login.html',
#                           {'error_msg': 'Invalid login details supplied.'})
#
#     else:
#         return render(request, 'rango/login.html')


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('rango:index'))


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


def track_url(request):
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
            except Page.DoesNotExist:
                return redirect('/rango/')
            else:
                page.views = page.views + 1
                page.save()
                return redirect(page.url)

    return redirect('/rango/')


@login_required
def register_profile(request):
    submitted = False
    if request.method == 'POST':
        user = request.user   # 用户相关信息保存在request.user中
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=user)
        if request.POST['website']:
            user_profile.website = request.POST['website']
            print('submit')
            submitted = True
        if 'picture' in request.FILES:
            user_profile.picture = request.FILES['picture']
            print('picture')
            submitted = True
        user_profile.save()

    return render(request, 'rango/profile_registration.html', {'submitted': submitted})


@login_required
def profile(request, username):
    true_user = 0
    context = {}
    try:
        user_query = User.objects.get(username=username)
        user_profile = UserProfile.objects.get(user=user_query)
    except User.DoesNotExist:
        pass
    except UserProfile.DoesNotExist:
        user = request.user
        if user == user_query:
            true_user = 1
    else:
        context['user_profile'] = user_profile
        user = request.user
        if user == user_query:
            true_user = 2

    context['true_user'] = true_user
    return render(request, 'rango/profile.html', context=context)


@login_required
def show_profile(request):
    context = {}
    try:
        users = User.objects.all().order_by('username')
    except User.DoesNotExist:
        pass
    else:
        context['users'] = users

    return render(request, 'rango/profile_show.html', context)


def about(request):
    # if request.session.test_cookie_worked():
    #     print('TEST COOKIE WORKED!')
    #     request.session.delete_test_cookie()
    print(request.method)
    print(request.user)
    context = {'creator': 'wangfp'}

    visitor_cookie_handler(request)
    context['visits'] = request.session.get('visits')
    return render(request, 'rango/about.html', context=context)