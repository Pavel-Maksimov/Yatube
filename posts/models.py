from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name="Название группы",
                             max_length=200,
                             help_text="Придумайте название для группы")
    slug = models.SlugField("Слаг", unique=True)
    description = models.TextField(verbose_name="Описание",
                                   help_text="Опишите группу")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст",
                            help_text="Напишите свой пост здесь")
    pub_date = models.DateTimeField(verbose_name="Дата публикации",
                                    auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор поста")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name="posts",
                              verbose_name="Группа",
                              help_text=("Выберите группу, в которой"
                                         " будет опубликован пост"),
                              blank=True,
                              null=True)
    image = models.ImageField(upload_to="posts/", blank=True, null=True,
                              help_text="Загрузите картинку к посту",
                              verbose_name="Изображение",)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name="Текст комментария",
                            help_text="Добавьте комментарий")
    created = models.DateTimeField(verbose_name="Дата",
                                   auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return (f"Коментарий {self.author} к посту"
                f"{self.post.id} от {self.created}")


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        ordering = ("user",)

    def __str__(self):
        return f"Пописка позоателя {self.user} на автора {self.author}"
