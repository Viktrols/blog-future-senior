import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from django.test import TestCase, Client

from ..models import Follow, Group, Post


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = get_user_model().objects.create_user(username='viki')
        cls.group = Group.objects.create(
            title='Название',
            slug='test-1',
            description='Текст')
        cls.post = Post.objects.create(
            author=cls.user,
            text='текст',
            group=cls.group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.user_2 = get_user_model().objects.create_user(username='user2')
        self.authorized_user_2 = Client()
        self.authorized_user_2.force_login(self.user_2)
        self.user_3 = get_user_model().objects.create_user(username='user3')
        self.authorized_user_3 = Client()
        self.authorized_user_3.force_login(self.user_3)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'follow.html': reverse('follow_index'),
            'group.html': reverse('group_posts', kwargs={'slug': 'test-1'}),
            'new.html': reverse('new_post'),
            'about/tech.html': reverse('about:tech'),
            'about/author.html': reverse('about:author'), }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.guest_client.get(reverse('index'))
        post = response.context.get('page')[0]
        self.assertEqual(post.text, 'текст')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)

    def test_group_post_content(self):
        response = self.guest_client.get(reverse('group_posts',
                                                 args=['test-1']))
        context = self.post
        expected_context = response.context.get('posts')[0]
        self.assertEqual(context, expected_context,
                         'Контекст group.html не верен')

    def test_post_view_context(self):
        response = self.authorized_user.get(
            reverse('post', kwargs={'username': self.user, 'post_id': 1}))
        context = self.post
        expected_context = response.context.get('post')
        self.assertEqual(context, expected_context)

    def test_new_post_form(self):
        fields_list = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_user.get(reverse('new_post'))
        for field, field_widget in fields_list.items():
            form_field = response.context.get('form').fields.get(field)
            self.assertIsInstance(form_field, field_widget)

    def test_post_edit_form(self):
        fields_list = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        response = self.authorized_user.get(
            reverse('post_edit', args=['viki', self.post.id]))

        for field, field_widget in fields_list.items():
            form_field = response.context.get('form').fields.get(field)
            self.assertIsInstance(form_field, field_widget)

    def test_create_content_index(self):
        new_post = Post.objects.create(
            text='текст',
            author=self.user,
            group=self.group
        )
        response = self.authorized_user.get(
            reverse('index'))
        self.assertContains(response, new_post)

    def test_create_content_group(self):
        new_post = Post.objects.create(
            text='текст2',
            author=self.user,
            group=self.group,)
        response = self.authorized_user.get(
            reverse('group_posts', args=[self.group.slug]))
        self.assertContains(response, new_post)

    def test_cache(self):
        response_1 = self.guest_client.get(reverse('index'))
        Post.objects.create(text='test2', author=self.user)
        response_2 = self.guest_client.get(reverse('index'))
        cache.clear()
        response_3 = self.guest_client.get(reverse('index'))
        self.assertEqual(response_1.content, response_2.content,
                         'Кэширование не работает')
        self.assertNotEqual(response_2.content, response_3.content,
                            'Кэш не очистился')

    def test_auth_user_can_comment(self):
        self.url_post = reverse('post', args=[self.user, self.post.id])
        self.url_comment = reverse('add_comment',
                                   args=[self.user, self.post.id]
                                   )

        self.authorized_user.post(self.url_comment, {'text': 'test_comment'})
        response = self.authorized_user.get(self.url_post)
        self.assertContains(response, 'test_comment')

    def test_index_image(self):
        Post.objects.create(
            text='test',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        response = self.authorized_user.get(reverse('index'))
        posts = response.context.get('page').object_list
        self.assertListEqual(list(posts), list(Post.objects.all()[:10]))

    def test_group_image(self):
        Post.objects.create(
            text='test',
            author=self.user,
            group=self.group,
            image=self.uploaded)
        response = self.authorized_user.get(reverse('group_posts',
                                            kwargs={'slug': 'test-1'}))
        posts = response.context.get('page').object_list
        self.assertListEqual(list(posts),
                             list(Post.objects.filter(author=self.user.id)))

    def test_profile_image(self):
        Post.objects.create(
            text='test',
            author=self.user,
            image=self.uploaded)
        response = self.authorized_user.get(
            reverse('profile', kwargs={'username': self.user}))

        posts = response.context.get('page').object_list
        self.assertListEqual(
            list(posts), list(Post.objects.filter(author=self.user.id)))

    def test_post_image(self):
        post = Post.objects.create(
            text='This is a test',
            author=self.user,
            group=self.group,
            image=self.uploaded
        )
        response = self.authorized_user.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user,
                    'post_id': post.pk
                }
            )
        )
        post_context = response.context['post']
        self.assertEqual(post_context.text, post.text)
        self.assertEqual(post_context.author, self.user)
        self.assertEqual(post_context.group, self.group)
        self.assertEqual(post_context.image, post.image)

    def test_follow_index(self):
        Post.objects.create(
            text='post',
            author=self.user_2
        )
        Follow.objects.create(user=self.user_2, author=self.user)
        response = self.authorized_user_2.get(reverse('follow_index'))
        posts = response.context.get('page').object_list
        self.assertListEqual(
            list(posts),
            list(Post.objects.filter(author=self.user.id)[:10])
        )

    def test_follow_index_not_behind_posts(self):
        Post.objects.create(
            text='post',
            author=self.user_2
        )
        Follow.objects.create(user=self.user_2, author=self.user)
        response_2 = self.authorized_user_3.get(reverse('follow_index'))
        posts_2 = response_2.context.get('page').object_list
        self.assertListEqual(
            list(posts_2),
            list(Post.objects.filter(author=self.user.id)[2:])
        )

    def test_follow(self):
        count_follow = Follow.objects.count()
        self.authorized_user.get(reverse('profile_follow',
                                 kwargs={'username': 'user2'}))
        count_following = Follow.objects.all().count()
        self.assertEqual(count_following, count_follow + 1)

    def test_unfollow(self):
        Follow.objects.create(user=self.user, author=self.user_2)
        count_follow = Follow.objects.count()
        self.authorized_user.get(reverse('profile_unfollow',
                                 kwargs={'username': 'user2'}))
        count_following = Follow.objects.all().count()
        self.assertEqual(count_following, count_follow - 1)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user('viki')

        cls.group = Group.objects.create(
            title='Название',
            slug='test-1',
            description='Текст')
        for i in range(13):
            Post.objects.create(
                text=f'тестовый текст{i}',
                author=cls.user,
                group=cls.group)

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_first_page(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_paginator_second_page(self):
        response = self.guest_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
