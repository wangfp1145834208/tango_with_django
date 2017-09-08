from django.shortcuts import render
from django.http import HttpResponse

from .models import Category, Page
from .forms import CategoryForm, PageForm


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context = {'categories': category_list,
               'pages': page_list}
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

def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    form  = PageForm()

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



def about(request):
    print(request.method)
    print(request.user)
    context = {'creator': 'wangfp'}
    return render(request, 'rango/about.html', context=context)