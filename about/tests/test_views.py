from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_access_by_name(self):
        """URL, генерируемые при помощи name, доступны
        для неавторизованного пользователя."""
        pages = [
            reverse("about: author"),
            reverse("about: tech")
        ]
        for page in pages:
            with self.subTest():
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе страниц about
        применяются соответствующие шаблоны."""
        names_templates = {
            "about: author": "about/author.html",
            "about: tech": "about/tech.html"
        }
        for name, template in names_templates.items():
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
