from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post, PostView
from .forms import PostForm, CommentForm, AuthorForm
from marketing.models import *
from django.db.models import Count, Q


# Create your views here.
# def get_author(user):
#     qs=Author.objects.filter(user=user)
#     if qs.exists():
#         return qs[0]
#     return None

def gallery(request):
    obj = Post.objects.all()
    context = {"pic": obj}
    return render(request, "gallery.html", context)


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
    context = {'queryset': queryset}
    return render(request, 'search_result.html', context)


def category_count():
    queryset = Post.objects.values('categories__title').annotate(Count('categories'))
    return queryset


def index(request):
    featured = Post.objects.published().filter(featured=True)
    latest = Post.objects.published().order_by('-published_date')[:3]

    if request.user.is_authenticated:
        qs = Post.objects.filter(author=request.user).order_by('-published_date')[:3]
        latest = (latest | qs).distinct()

    if request.user.is_authenticated:
        qs = Post.objects.filter(author=request.user).order_by('-published_date')
        featured = (featured | qs).distinct()

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            new_signup = Signup()
            new_signup.email = email
            new_signup.save()
    context = {
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'index.html', context)


def blog(request):
    cat_count = category_count()
    most_recent = Post.objects.published().order_by('-published_date')[:3]
    post_list = Post.objects.published()

    if request.user.is_authenticated:
        qs = Post.objects.filter(author=request.user).order_by('-published_date')
        post_list = (post_list | qs).distinct()

    if request.user.is_authenticated:
        qs = Post.objects.filter(author=request.user).order_by('-published_date')[:3]
        most_recent = (most_recent | qs).distinct()

    paginator = Paginator(post_list, 2)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        'page_request_var': page_request_var,
        'most_recent': most_recent,
        'queryset': queryset,
        'cat_count': cat_count
    }
    return render(request, 'blog.html', context)


def post_detail(request, id):
    cat_count = category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
    context = {
        'form': form,
        'post': post,
        'most_recent': most_recent,
        'cat_count': cat_count
    }
    return render(request, 'post.html', context)


@login_required
def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    # author=get_author(request.user)

    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


@login_required
def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    # author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


@login_required
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")
    post.delete()
    return redirect(reverse("index"))


@login_required
def contact(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('index')
    else:
        form = AuthorForm()
    context = {'form': form}
    return render(request, 'contact.html', context)


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.post = post
            obj.save()
            return redirect(reverse('post-detail', kwargs={'id': post.id}))
