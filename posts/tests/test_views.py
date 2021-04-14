import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post

from . import constants as const

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаём пользователя (автор поста),
        пост, опубликованный в группе, и чужую группу, где пост
        не должен отображаться"""
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=const.USERNAME)
        cls.test_group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=const.SMALL_GIF,
            content_type="image/gif"
        )
        cls.test_post = Post.objects.create(
            text=const.POST_TEXT,
            author=User.objects.get(username=const.USERNAME),
            group=PostPagesTests.test_group,
            image=uploaded
        )
        cls.strange_test_group = Group.objects.create(
            title=const.STRANGE_GROUP_TITLE,
            slug=const.STRANGE_GROUP_SLUG,
            description=const.STRANGE_GROUP_DESCRIPTION
        )
        cls.POST_URL = reverse("post", kwargs={
            "username": const.USERNAME,
            "post_id": PostPagesTests.test_post.id
        }
        )
        cls.POST_EDIT_URL = reverse("post_edit", kwargs={
            "username": const.USERNAME,
            "post_id": PostPagesTests.test_post.id
        }
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.test_user)

    def test_home_page_shows_correct_context(self):
        """Шаблон домашней страницы сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(reverse("index"))
        first_post = response.context["page"][0]
        self.assertEqual(first_post.text, const.POST_TEXT)
        self.assertEqual(first_post.author, PostPagesTests.test_user)
        self.assertEqual(first_post.group, PostPagesTests.test_group)
        self.assertEqual(first_post.image, PostPagesTests.test_post.image)

    def test_group_page_shows_correct_context(self):
        """Шаблон страницы группы сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(const.GROUP_URL)
        first_post = response.context["page"][0]
        group = response.context["group"]
        self.assertEqual(first_post.text, const.POST_TEXT)
        self.assertEqual(first_post.author, PostPagesTests.test_user)
        self.assertEqual(first_post.group, PostPagesTests.test_group)
        self.assertEqual(first_post.image, PostPagesTests.test_post.image)
        self.assertEqual(group.title, const.GROUP_TITLE)
        self.assertEqual(group.slug, const.GROUP_SLUG)
        self.assertEqual(group.description, const.GROUP_DESCRIPTION)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон страницы создания нового поста
        сформирован с правильным контекстом"""
        response = self.authorized_client.get(const.NEW_POST_URL)
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField
        }
        for field, field_class in form_fields.items():
            with self.subTest():
                form_field = response.context["form"].fields[field]
                self.assertIsInstance(form_field, field_class)

    def test_profile_shows_correct_context(self):
        """Шаблон страницы профиля сформирован
        с правильным контекстом"""
        response = self.authorized_client.get(const.PROFILE_URL)
        first_post = response.context["page"][0]
        profile_user = response.context["author"]
        self.assertEqual(first_post.text, const.POST_TEXT)
        self.assertEqual(first_post.author, PostPagesTests.test_user)
        self.assertEqual(first_post.group, PostPagesTests.test_group)
        self.assertEqual(first_post.image, PostPagesTests.test_post.image)
        self.assertEqual(profile_user, PostPagesTests.test_user)

    def test_post_page_shows_correct_context(self):
        """Шаблон страницы просмотра записи
        сформирован с правильным контекстом"""
        response = self.authorized_client.get(PostPagesTests.POST_URL)
        author = response.context["author"]
        post = response.context["post"]
        self.assertEqual(author, PostPagesTests.test_post.author)
        self.assertEqual(post, PostPagesTests.test_post)
        self.assertEqual(post.image, PostPagesTests.test_post.image)

    def test_post_edit_page_shows_correct_context(self):
        """При редактировании записи в форму заносятся
        данные соответствующей записи"""
        response = self.authorized_client.get(PostPagesTests.POST_EDIT_URL)
        form_text = response.context["form"].instance.text
        form_group = response.context["form"].instance.group
        form_image = response.context["form"].instance.image
        self.assertEqual(form_text, PostPagesTests.test_post.text)
        self.assertEqual(form_group, PostPagesTests.test_post.group)
        self.assertEqual(form_image, PostPagesTests.test_post.image)

    def test_post_at_home_page(self):
        """Тестовый пост появляется на главной странице"""
        response = self.authorized_client.get(const.HOME_URL)
        posts = response.context["page"]
        self.assertIn(PostPagesTests.test_post, posts)

    def test_post_at_group_page(self):
        """Тестовый пост появляется на странице группы, в
        которую он включён"""
        response = self.authorized_client.get(const.GROUP_URL)
        posts = response.context["page"]
        self.assertIn(PostPagesTests.test_post, posts)

    def test_post_not_at_strange_group_page(self):
        """Тестовый пост не появляется на странице чужой группы,
        в которую он не включён"""
        response = self.authorized_client.get(const.STRANGE_GROUP_URL)
        posts = response.context["page"]
        self.assertNotIn(PostPagesTests.test_post, posts)


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=const.USERNAME)
        cls.test_group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )
        new_posts = []
        for i in range(11):
            new_posts.append(Post(
                text=f"Текст записи {i}",
                author=PaginatorViewTests.test_user,
                group=PaginatorViewTests.test_group,
            ))
        Post.objects.bulk_create(new_posts)

    def setUp(self):
        self.client = Client()
        self.pages = [
            const.HOME_URL,
            const.GROUP_URL,
        ]

    def test_pages_contain_correct_number_of_posts(self):
        for page in self.pages:
            with self.subTest():
                response_first_page = self.client.get(page)
                response_second_page = self.client.get(page + "?page=2")
                first_page_posts = response_first_page.context["page"]
                second_page_posts = response_second_page.context["page"]
                self.assertEqual(len(first_page_posts), 10)
                self.assertEqual(len(second_page_posts), 1)


class ErrorCodesReturn(TestCase):
    def setUp(self):
        self.client = Client()

    def test_not_found_page_return_404(self):
        response = self.client.get("/unknown_page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "misc/404.html")


class CacheUseTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=const.USERNAME)
        cls.test_post = Post.objects.create(
            text=const.POST_TEXT,
            author=User.objects.get(username=const.USERNAME)
        )

    def setUp(self):
        self.client = Client()

    def test_home_page_uses_cache(self):
        """Контент не меняется до очистки кэша"""
        response_before_creating_post = self.client.get(const.HOME_URL)
        Post.objects.create(
            text=const.POST_TEXT,
            author=User.objects.get(username=const.USERNAME)
        )
        response_after_creating_post = self.client.get(const.HOME_URL)
        cache.clear()
        response_after_cache_clearing = self.client.get(const.HOME_URL)
        self.assertEqual(response_before_creating_post.content,
                         response_after_creating_post.content)
        self.assertNotEqual(response_after_creating_post.content,
                            response_after_cache_clearing.content)


class UsersFollowingTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username=const.USERNAME)
        cls.author = User.objects.create_user(username=const.AUTHOR_USERNAME)
        cls.test_post = Post.objects.create(
            text=const.POST_TEXT,
            author=UsersFollowingTest.author
        )

    def setUp(self):
        self.user_client = Client()
        self.user_client.force_login(UsersFollowingTest.test_user)
        self.author_client = Client()
        self.author_client.force_login(UsersFollowingTest.author)

    def test_user_can_follow_other_user(self):
        """При подписке пользователя на другого пользователя
        создается объект Follow"""
        self.user_client.get(const.FOLLOW_URL)
        follow = Follow.objects.filter(
            user=UsersFollowingTest.test_user,
            author=UsersFollowingTest.author)
        self.assertTrue(follow.exists())

    def test_new_post_appears_for_followers(self):
        """При подписке пользователя на другого пользователя новый
        пост отображается в ленте подписанных пользователей
        и не отображается при отписке"""
        self.user_client.get(const.FOLLOW_URL)
        response = self.user_client.get(const.FOLLOW_INDEX_URL)
        self.assertEqual(len(response.context["page"]), 1)
        self.user_client.get(const.UNFOLLOW_URL)
        response = self.user_client.get(const.FOLLOW_INDEX_URL)
        self.assertEqual(len(response.context["page"]), 0)
