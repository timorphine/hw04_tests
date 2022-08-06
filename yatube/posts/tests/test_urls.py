from django.contrib.auth import get_user_model
from django.test import TestCase, Client


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
        # Гость
        self.guest_client = Client()
        # Авторизованный cls.user, он же автор
        self.autorized_client = Client()
        self.autorized_client.force_login(PostsURLTests.user)
        # Другой пользователь с ником non_author
        self.not_author_client = Client()
        self.not_author_client.force_login(PostsURLTests.not_author)

    def test_home_page_response(self):
        """Тест ответа домашней страницы."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_page_response(self):
        """Тест ответа страницы с группами."""
        response = self.guest_client.get('/group/Test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_response(self):
        """Тест ответа страницы профиля"""
        response = self.guest_client.get('/profile/Author/')
        self.assertEqual(response.status_code, 200)

    def test_post_detail_reponse(self):
        """Тест ответа страницы с подробностями поста."""
        response = self.guest_client.get(f'/posts/{PostsURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page_response(self):
        """Тест ответа несуществующей страницы."""
        response = self.guest_client.get('/unexisted_page/')
        self.assertEqual(response.status_code, 404)

    def test_create_page_for_not_auth(self):
        """Тест редиректа со страницы create для неавторизованного юзера."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_create_page_for_auth(self):
        """Тест ответа страницы create для авторизованного юзера."""
        response = self.autorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit_for_non_author(self):
        """Редактирование поста доступно только для автора."""
        # Автор получает респонс 200, неавтора - редиректит
        response = self.not_author_client.get(
            f'/posts/{PostsURLTests.post.id}/edit/'
        )
        self.assertRedirects(
            response, '/profile/not_author/')

    def test_urls_leads_right_templates(self):
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/Test-slug/': 'posts/group_list.html',
            '/profile/not_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.autorized_client.get(address)
                self.assertTemplateUsed(response, template)
