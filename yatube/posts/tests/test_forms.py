from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='TestText'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateForm.user)

    def test_post_goes_in_database(self):
        """Проверяем появление поста в БД при создании и редирект"""
        obj_count = Post.objects.count()
        post_form = {
            'author': 'TestUser',
            'text': 'AnotherText'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_form,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'TestUser'}
            )
        )
        self.assertEqual(Post.objects.count(), obj_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateForm.post.author,
                text=PostCreateForm.post.text
            ).exists()
        )

    def test_edited_post(self):
        """Проверяем изменение поста в БД после редакции"""
        obj_count = Post.objects.count()
        post_form = {
            'author': 'TestUser',
            'text': 'AnotherText',
            'group': 'TestGroup'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=[PostCreateForm.post.id]
            ),
            data=post_form,
            follow=True

        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=[PostCreateForm.post.id]
            )
        )
        self.assertEqual(Post.objects.count(), obj_count)
        self.assertEqual(
            Post.objects.get(PostCreateForm.post.id).author,
            PostCreateForm.post.author
        )
        self.assertEqual(
            Post.objects.get(PostCreateForm.post.id).text,
            post_form['text']
        )
