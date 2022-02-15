from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

from . import constants as const

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.general_user = User.objects.create_user(username="test_user")
        cls.author = User.objects.create_user(username=const.USERNAME)
        cls.test_group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )
        cls.test_post = Post.objects.create(
            text=const.POST_TEXT,
            author=PostURLTests.author,
            group=PostURLTests.test_group
        )
        cls.POST_URL = reverse("posts:post", kwargs={
            "username": const.USERNAME,
            "post_id": PostURLTests.test_post.id
        }
        )
        cls.POST_EDIT_URL = reverse("posts:post_edit", kwargs={
            "username": const.USERNAME,
            "post_id": PostURLTests.test_post.id
        }
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.profile_owner_client = Client()
        self.authorized_client.force_login(PostURLTests.general_user)
        self.profile_owner_client.force_login(PostURLTests.author)

    def test_names_correspond_urls(self):
        """Имена страниц соответствуют явным URL"""
        names_urls = {
            const.HOME_URL: "/",
            const.GROUP_URL: f"/group/{PostURLTests.test_group.slug}/",
            const.NEW_POST_URL: "/new/",
            const.PROFILE_URL: f"/{PostURLTests.author.username}/",
            PostURLTests.POST_URL:
            f"/{PostURLTests.author.username}/{PostURLTests.test_post.id}/",
            PostURLTests.POST_EDIT_URL:
            f"/{PostURLTests.author.username}/"
            f"{PostURLTests.test_post.id}/edit/"
        }
        for name, url in names_urls.items():
            with self.subTest():
                self.assertEqual(name, url)

    def test_pages_availability_through_url(self):
        """Страницы доступны по соответствующим URL"""
        guest_available_pages = [
            const.HOME_URL,
            const.GROUP_URL,
            const.PROFILE_URL,
            PostURLTests.POST_URL,
        ]
        general_authorized_available_pages = [
            PostURLTests.POST_URL,
        ]
        profile_owner_available_pages = [
            PostURLTests.POST_EDIT_URL,
        ]
        client_pages_access = {
            self.guest_client: guest_available_pages,
            self.authorized_client: general_authorized_available_pages,
            self.profile_owner_client: profile_owner_available_pages
        }
        for client, pages in client_pages_access.items():
            for page in pages:
                with self.subTest():
                    response = client.get(page)
                    self.assertEqual(response.status_code, 200)

    def test_redirections_for_guest(self):
        """Страницы, недоступные неавторизованному
        пользователю, перенаправят его на страницу регистрации"""
        guest_redirections = {
            const.NEW_POST_URL: (const.LOGIN_URL
                                 + "?next="
                                 + const.NEW_POST_URL),
        }
        for page, redirection in guest_redirections.items():
            with self.subTest():
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(response, redirection)

    def test_redirections_for_general_user(self):
        """Страницы, доступные только автору записи, перенаправляют
        других авторизованных пользователей на страницу просмотра записи"""
        general_user_redirections = {
            PostURLTests.POST_EDIT_URL: PostURLTests.POST_URL
        }
        for page, redirection in general_user_redirections.items():
            with self.subTest():
                response = self.authorized_client.get(page, follow=True)
                self.assertRedirects(response, redirection)

    def test_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        url_templates = {
            const.HOME_URL: "index.html",
            const.NEW_POST_URL: "new_post.html",
            const.GROUP_URL: "group.html",
            PostURLTests.POST_URL: "post.html",
            PostURLTests.POST_EDIT_URL: "new_post.html"
        }
        for url, template in url_templates.items():
            with self.subTest():
                response = self.profile_owner_client.get(url)
                self.assertTemplateUsed(response, template)
