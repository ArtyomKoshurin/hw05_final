from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm
from .utils import CastomPaginator


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = CastomPaginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = CastomPaginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not follow.exists():
        Follow.objects.create(user=request.user, author=author)
    posts = author.posts.all()
    page_obj = CastomPaginator(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': True,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user_id=request.user, author=author)
    if following.exists():
        following.delete()
    posts = author.posts.all()
    page_obj = CastomPaginator(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': False,
    }
    return render(request, 'posts/profile.html', context)


def group_posts(request, any_slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=any_slug)
    posts = group.posts.all()
    page_obj = CastomPaginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = CastomPaginator(request, posts)
    if request.user.is_authenticated is True:
        follower = Follow.objects.filter(user_id=request.user, author=author)
        if request.user != author and not follower.exists():
            following = False
        else:
            following = True
        context = {
            'author': author,
            'page_obj': page_obj,
            'following': following,
        }
    else:
        context = {
            'author': author,
            'page_obj': page_obj,
        }
    return render(request, 'posts/profile.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)
