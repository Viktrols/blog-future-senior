from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Group, Post, Comment, Follow, Profile


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(username='Viki')
        cls.user_2 = get_user_model().objects.create_user(username='Ivan')
        cls.group = Group.objects.create(
            title='Название группы',
            slug='test-1',
            description='текст'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            title = 'заголовок',
            text='текст',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post = cls.post,
            author = cls.user,
            text='Текст комментария'
        )

        cls.follow = Follow.objects.create(
            user = cls.user,
            author = cls.user_2
        )
        cls.profile = Profile.objects.create(
            user = cls.user,
        )

    def test_verbose_post(self):
        field_verbose = {
            'text': 'Текст',
            'group': 'Группа',
            'title': 'Заголовок'
        }
        for field, value in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(self.post._meta.get_field(field).verbose_name,
                                 value, 'Исправьте verbose name в модели Post')

    def test_verbose_group(self):
        field_verbose = {
            'title': 'Название группы',
        }
        for field, value in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(self.group._meta.get_field(field).
                                 verbose_name,
                                 value, 'Исправьте verbose в модели Group')

    def test_verbose_comment(self):
        field_verbose = {
            'post': 'Пост с комментариями',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата публикации'
        }
        for field, value in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(self.comment._meta.get_field(field).
                                 verbose_name,
                                 value, 'Исправьте verbose в модели Comment')

    def test_verbose_follow(self):
        field_verbose = {
            'user': 'Тот, на кого подписаны',
            'author': 'Подписчик'
        }
        for field, value in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(self.follow._meta.get_field(field).
                                 verbose_name,
                                 value, 'Исправьте verbose в модели Follow')

    def test_verbose_profile(self):
        field_verbose = {
            'bio': 'Описание профиля',
            'image': 'Аватар'
        }
        for field, value in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(self.profile._meta.get_field(field).
                                 verbose_name,
                                 value, 'Исправьте verbose в модели Profile')

    def test_help_text_post(self):
        field_help_text = {
            'text': 'Напишите свой пост здесь',
            'group': 'Выберите группу (не обязательно)'
        }
        for field, value in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(self.post._meta.get_field(field).help_text,
                                 value, 'Исправьте help text в модели Post')

    def test_post_str_(self):
        value = self.post.__str__()
        expected = self.post.text[:15]
        self.assertEqual(value, expected,
                         'Метод __str__ модели Post работает не правильно.')

    def test_group_str_(self):
        value = self.group.__str__()
        expected = self.group.title
        self.assertEqual(value, expected,
                         'Метод __str__ модели Group работает не правильно.')
    
    def test_comment_str_(self):
        value = self.comment.__str__()
        expected = self.comment.text[:15]
        self.assertEqual(value, expected,
                         'Метод __str__ модели Comment работает не правильно.')
