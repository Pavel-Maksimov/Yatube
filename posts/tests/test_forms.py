import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

from . import constants as const

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=const.USERNAME)
        cls.test_group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )
        cls.test_post = Post.objects.create(
            text=const.POST_TEXT,
            author=PostCreateFormTests.test_user,
            group=PostCreateFormTests.test_group
        )
        cls.POST_URL = reverse("posts:post", kwargs={
            "username": const.USERNAME,
            "post_id": PostCreateFormTests.test_post.id
        }
        )
        cls.POST_EDIT_URL = reverse("posts:post_edit", kwargs={
            "username": const.USERNAME,
            "post_id": PostCreateFormTests.test_post.id
        }
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.test_user)

    def test_create_post(self):
        """Проверяем редирект при добавлении поста,
        что количество постов увеличивается на 1,
        что созданный пост существует в базе данных"""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=const.SMALL_GIF,
            content_type="image/gif"
        )
        form_data = {
            "text": "Текст нового поста",
            "image": uploaded
        }
        response = self.authorized_client.post(
            const.NEW_POST_URL, data=form_data, follow=True)
        self.assertRedirects(response, const.HOME_URL)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text="Текст нового поста",
        ).exists()
        )

    def test_edit_post(self):
        """Проверяем редирект при изменении поста
        и что текст поста изменился"""
        post_id = PostCreateFormTests.test_post.id
        post_edit_page = PostCreateFormTests.POST_EDIT_URL
        redirection_page = PostCreateFormTests.POST_URL
        initial_text = Post.objects.get(id=post_id).text
        new_form_data = {
            "text": "Изменённый текст тестового поста",
        }
        response = self.authorized_client.post(
            post_edit_page, data=new_form_data, follow=True)
        self.assertRedirects(response, redirection_page)
        self.assertNotEqual(initial_text, Post.objects.get(id=post_id).text)


class CommentCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.general_user = User.objects.create_user(username=const.USERNAME)
        cls.author = User.objects.create_user(username=const.AUTHOR_USERNAME)
        cls.test_group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )
        cls.test_post = Post.objects.create(
            text=const.POST_TEXT,
            author=CommentCreateTests.author,
            group=CommentCreateTests.test_group
        )
        cls.POST_URL = reverse("posts:post", args=(
            const.AUTHOR_USERNAME,
            CommentCreateTests.test_post.id,
        )
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.profile_owner_client = Client()
        self.authorized_client.force_login(CommentCreateTests.general_user)
        self.profile_owner_client.force_login(CommentCreateTests.author)

    def test_comments_adding(self):
        """Только авторизованный пользователь
        может комментировать посты"""
        form_data = {
            "text": "Текст нового поста"
        }
        add_comment_url = reverse("posts:add_comment",
                                  args=(const.AUTHOR_USERNAME,
                                        CommentCreateTests.test_post.id,))
        self.guest_client.post(add_comment_url,
                               data=form_data,
                               follow=True)
        comments = Comment.objects.filter(
            post=CommentCreateTests.test_post.id)
        self.assertFalse(comments.exists())
        self.authorized_client.post(add_comment_url,
                                    data=form_data,
                                    follow=True)
        comments = Comment.objects.filter(
            post=CommentCreateTests.test_post.id)
        self.assertTrue(comments.exists())
