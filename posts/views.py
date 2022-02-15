from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from yatube.settings import PAGINATOR_NUMBER

from .decorators import check_user_is_author
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.prefetch_related("author",
                                              "group").all()
    paginator = Paginator(post_list, PAGINATOR_NUMBER)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {"page": page, "path": "home"}
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.prefetch_related("author",
                                             "group").all()
    paginator = Paginator(post_list, PAGINATOR_NUMBER)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST" and form.is_valid():
        text = form.cleaned_data["text"]
        group = form.cleaned_data["group"]
        image = form.cleaned_data["image"]
        post = Post(text=text, group=group, author=request.user, image=image)
        post.save()
        return redirect(reverse("posts:index"))
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username__iexact=username)
    post_list = Post.objects.select_related("author",
                                            "group").filter(author=author)
    paginator = Paginator(post_list, PAGINATOR_NUMBER)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author, user=request.user).exists()
    context = {"author": author, "page": page, "following": following}
    if request.user == author:
        context["path"] = "my_profile"
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    author = User.objects.get(username__iexact=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    comment_form = CommentForm()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author, user=request.user).exists()
    context = {
        "author": author,
        "post": post,
        "comment_form": comment_form,
        "following": following
    }
    return render(request, "post.html", context)


@check_user_is_author
def post_edit(request, username, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect(reverse(
                "posts:post",
                kwargs={"username": username, "post_id": post.id}
            ))
    form = PostForm(instance=post)
    return render(request, "new_post.html", {"form": form, "post": post})


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        text = form.cleaned_data["text"]
        post = Post.objects.get(id=post_id)
        author = request.user
        comment = Comment(text=text, post=post, author=author)
        comment.save()
    return redirect(reverse("posts:post", args=(username, post_id)))


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    authors = User.objects.filter(following__in=follows)
    posts = Post.objects.prefetch_related(
        "author",
        "group").filter(author__in=authors)
    paginator = Paginator(posts, PAGINATOR_NUMBER)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    follow_exists = Follow.objects.filter(author=author,
                                          user=request.user).exists()
    if request.user != author and not follow_exists:
        follow = Follow.objects.create(author=author, user=request.user)
        follow.save()
    return redirect(reverse("posts:profile", args=(username,)))


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.get(author=author, user=request.user)
    follow.delete()
    return redirect(reverse("posts:profile", args=(username,)))


@login_required
def my_follows(request):
    follows = Follow.objects.filter(user=request.user)
    users = User.objects.filter(following__in=follows)
    print('users:', users)
    paginator = Paginator(users, PAGINATOR_NUMBER)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {"page": page, "path": "my_follows"}
    return render(request, "follow_list.html", context)
