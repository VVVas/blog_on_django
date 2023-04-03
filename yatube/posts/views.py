from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import paginate

User = get_user_model()


def index(request):
    post_list = Post.objects.prefetch_related(
        'author',
        'group',
    )
    page_obj = paginate(post_list, request.GET.get('page'))
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related(
        'author',
    )
    page_obj = paginate(post_list, request.GET.get('page'))
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related(
        'group',
    )
    post_count = post_list.count()
    page_obj = paginate(post_list, request.GET.get('page'))
    template = 'posts/profile.html'
    context = {
        'author': author,
        'post_count': post_count,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    post_count = author.posts.count()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'post_count': post_count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
        return render(request, template, {'form': form})
    else:
        form = PostForm()
        return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('posts:post_detail', post_id)
        else:
            form = PostForm(instance=post)
        return render(request, template, {'form': form, 'is_edit': 'is_edit'})
    return redirect('posts:post_detail', post_id)
