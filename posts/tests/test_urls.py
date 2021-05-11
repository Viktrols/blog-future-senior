from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create_user(username='viki')

        cls.list_pages = {
            reverse('index'): 'index.html',
            reverse('group_posts', args=['test-1']): 'group.html',
            reverse('profile', args=[cls.user]): 'profile.html',
            reverse('post', args=[cls.user, 1]): 'post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        cls.group = Group.objects.create(
            title='Название',
            slug='test-1',
            description='Текст')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_urls(self):
        for page, templates in self.list_pages.items():
            response = self.guest_client.get(page)
            self.assertEqual(response.status_code, 200,
                             f'Страница {page} не работает')

    def test_templates(self):
        for page, templates in self.list_pages.items():
            response = self.guest_client.get(page)
            self.assertTemplateUsed(response, templates,
                                    f'Шаблон {templates} не работает')

    def test_authorised_useer_new_post(self):
        response = self.authorized_user.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_authorised_user_post_edit(self):
        response = self.authorized_user.get(
            reverse('post_edit', args=[self.user, 1]))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_user_new_post_redirect(self):
        response = self.guest_client.get(reverse('new_post'))
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_unauthorized_user_post_edit_redirect(self):
        response = self.guest_client.get(reverse('post_edit',
                                         args=[self.user, 1]))
        self.assertRedirects(response, '/auth/login/?next=/viki/1/edit/')

    def test_404(self):
        response = self.guest_client.get('test')
        self.assertEqual(response.status_code, 404)
