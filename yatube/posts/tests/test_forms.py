from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

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
        self.authorized_client.force_login(self.user)

    def test_authorized_user_can_make_post(self):
        """Проверяем возможность создания поста авторизованным пользователем"""
        obj_count = Post.objects.count()
        post_form = {
            'group': self.group.id,
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
                kwargs={'username': self.user}
            )
        )
        self.assertEqual(Post.objects.count(), obj_count + 1)
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, post_form['text'])
        self.assertEqual(last_post.group, self.post.group)
        self.assertEqual(last_post.author, self.post.author)

    def test_edit_post(self):
        """Проверяем изменение поста в БД после редакции"""
        obj_count = Post.objects.count()
        changed_post_form = {
            'group': self.group.id,
            'text': 'OneMoreText'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=[self.post.id]
            ),
            data=changed_post_form,
            follow=True

        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), obj_count)
        self.assertTrue(
            Post.objects.filter(
                text=changed_post_form['text']
            ).exists()
        )
        changed_post = Post.objects.get(id=1)
        self.assertEqual(changed_post.text, changed_post_form['text'])
        self.assertEqual(changed_post.group, self.post.group)
        self.assertEqual(changed_post.author, self.post.author)
