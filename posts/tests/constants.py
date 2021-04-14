from django.urls import reverse


GROUP_SLUG = "test_group"
GROUP_NAME = "test_group"
GROUP_TITLE = "Тестовая группа"
GROUP_DESCRIPTION = "Описание тестовой группы"

STRANGE_GROUP_SLUG = "strange_group"
STRANGE_GROUP_NAME = "strange_group"
STRANGE_GROUP_TITLE = "Чужая естовая группа"
STRANGE_GROUP_DESCRIPTION = "Описание чужой тестовой группы"

USERNAME = "username"
AUTHOR_USERNAME = "author"

POST_VERBOSES = {
    "text": "Текст",
    "pub_date": "Дата публикации",
    "author": "Автор поста",
    "group": "Группа"
}
POST_HELP_TEXTS = {
    "text": "Напишите свой пост здесь",
    "group": "Выберите группу, в которой будет опубликован пост"
}
POST_TEXT = "Текст чужой тестового поста"

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

HOME_URL = reverse("index")
NEW_POST_URL = reverse("new_post")
GROUP_URL = reverse("group_posts", kwargs={"slug": GROUP_SLUG})
STRANGE_GROUP_URL = reverse("group_posts",
                            kwargs={"slug": STRANGE_GROUP_SLUG})
PROFILE_URL = reverse("profile", kwargs={"username": USERNAME})
LOGIN_URL = reverse("login")
FOLLOW_URL = reverse("profile_follow", args=(AUTHOR_USERNAME,))
UNFOLLOW_URL = reverse("profile_unfollow", args=(AUTHOR_USERNAME,))
FOLLOW_INDEX_URL = reverse("follow_index")
