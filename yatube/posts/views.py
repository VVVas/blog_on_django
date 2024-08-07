from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from .utils import paginate

User = get_user_model()


def index(request):
    """Лента всех публикаций"""
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
    """Лента публикаций сообщества."""
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
    """Профиль пользователя и лента его публикаций."""
    author = get_object_or_404(User, username=username)
    user = request.user
    post_list = author.posts.select_related(
        'group',
    )
    page_obj = paginate(post_list, request.GET.get('page'))
    following = True
    if user.is_authenticated and author != user:
        following = Follow.objects.filter(user=user, author=author).exists()
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница публикации."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related(
        'author',
    )
    page_obj = paginate(comments, request.GET.get('page'))
    form = CommentForm()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Создание публикации."""
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None
        )
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
    """Редактирование публикации."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(
                request.POST or None,
                files=request.FILES or None,
                instance=post
            )
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('posts:post_detail', post_id)
        else:
            form = PostForm(instance=post)
        return render(request, template, {'form': form, 'is_edit': True})
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    """Лента публикаций избранных авторов."""
    author_list = request.user.follower.values('author')
    post_list = Post.objects.filter(author__in=author_list).select_related(
        'group',
    )
    page_obj = paginate(post_list, request.GET.get('page'))
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:profile', username=username)
