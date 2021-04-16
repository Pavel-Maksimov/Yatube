from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

from .models import Post, User

User = get_user_model()


def check_user_is_author(func):
    """Функция-декоратор проверяет,
    является ли пользователь автором поста"""
    def check_user(request, username, post_id, *args, **kwargs):
        post = Post.objects.get(id=post_id)
        if request.user == post.author:
            return func(request, username, post_id, *args, **kwargs)
        return redirect(reverse("post",
                                kwargs={"username": username,
                                        "post_id": post.id
                                        }
                                )
                        )
    return check_user
