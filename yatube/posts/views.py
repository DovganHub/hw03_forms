from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Group
from django.contrib.auth import get_user_model
from .forms import PostForm
from django.template import RequestContext

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    count = paginator.count
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'username': username,
        'page_obj': page_obj,
        'count': count,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.filter(pk=post_id).first()
    post_list = Post.objects.filter(author=post.author)
    paginator = Paginator(post_list, 10)
    count = paginator.count
    context = {
        'post_id': post_id,
        'post': post,
        'count': count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    user = request.user
    form = PostForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = user
        obj.save()
        return redirect(f'/profile/{user}/')
    form = PostForm()
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create.html', context,
                  RequestContext(request))


def post_edit(request, post_id):
    user = request.user
    post = Post.objects.filter(pk=post_id).first()
    if request.user.is_authenticated and user == post.author:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}')
        else:
            form = PostForm(instance=post)

        form = PostForm(instance=post)
        form.text = post.text
        context = {
            'form': form,
            'is_edit': True,
        }
        return render(request, 'posts/create.html', context,
                      RequestContext(request))
    return redirect(f'/posts/{post_id}')
