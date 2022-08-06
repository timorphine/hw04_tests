from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .pagination import paginator_context


def index(request):
    context = paginator_context(Post.objects.all(), request)
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        "group": group
    }
    context.update(paginator_context(
        Post.objects.all().filter(group=group),
        request)
    )
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_count = Post.objects.all(
    ).filter(author=author).count()
    context = {
        "author": author,
        "post_count": post_count
    }
    context.update(paginator_context(
        Post.objects.all().filter(author=author),
        request)
    )
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_list = Post.objects.all().filter(author_id=post.author).count()
    context = {
        "post": post,
        "post_list": post_list
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.id and request.user != post.author:
        return redirect('posts:profile', request.user)
    is_edit = True
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        "form": form,
        "is_edit": is_edit
    }
    return render(request, 'posts/create_post.html', context)
