from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

from . import constants as const

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test_author = User.objects.create_user(username=const.USERNAME)
        test_group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(author=test_author,
                                       text=const.POST_TEXT,
                                       group=test_group)

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = const.POST_VERBOSES
        for field, expected in field_verboses.items():
            with self.subTest(value=field):
                verbose_name = post._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = const.POST_HELP_TEXTS
        for field, expected in field_help_texts.items():
            with self.subTest(value=field):
                help_text = post._meta.get_field(field).help_text
                self.assertEqual(help_text, expected)

    def test_object_name(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=const.GROUP_TITLE,
            slug=const.GROUP_SLUG,
            description=const.GROUP_DESCRIPTION
        )

    def test_object_name(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name)
