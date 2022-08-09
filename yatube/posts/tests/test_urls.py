from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='Test-slug'
        )
        cls.post = Post.objects.create(
            text='TestPost',
            group=cls.group,
            author=cls.user
        )

    def setUp(self):
        self.autorized_client = Client()
        self.autorized_client.force_login(PostsURLTests.user)
        self.not_author_client = Client()
        self.not_author_client.force_login(PostsURLTests.not_author)

    def test_home_page_response(self):
        """Тест ответа домашней страницы."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_page_response(self):
        """Тест ответа страницы с группами."""
        response = self.client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_response(self):
        """Тест ответа страницы профиля"""
        response = self.client.get(f'/profile/{self.user}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_reponse(self):
        """Тест ответа страницы с подробностями поста."""
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_response(self):
        """Тест ответа несуществующей страницы."""
        response = self.client.get('/unexisted_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_page_for_not_auth(self):
        """Тест редиректа со страницы create для неавторизованного юзера."""
        response = self.client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_create_page_for_auth(self):
        """Тест ответа страницы create для авторизованного юзера."""
        response = self.autorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_guest(self):
        self.guest_client = Client()
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_edit_for_non_author(self):
        """Редактирование поста доступно только для автора."""
        response = self.not_author_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response, f'/profile/{self.not_author}/')

    def test_urls_leads_to_right_templates(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/Test-slug/': 'posts/group_list.html',
            '/profile/not_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.autorized_client.get(address)
                self.assertTemplateUsed(response, template)
