from django.test import TestCase, Client
from ..models import Group, Post
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.form = PostCreateFormTests()

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.user = User.objects.create_user('test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_works_correctly(self):
        post_count = Post.objects.count()
        form = {
            'text': 'Текст нового поста',
            'group': PostCreateFormTests.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form,
            # follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Текст нового поста',
            ).exists()
        )

    def test_post_edit_works_correctly(self):
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        previous_text = self.post
        self.newgroup = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group',
            description='Описание'
        )
        form_data = {
            'text': 'Новый текст формы',
            'group': self.newgroup.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': previous_text.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            author=self.user,
            group=self.newgroup.id,
            pub_date=self.post.pub_date
        ).exists()
        )
        self.assertNotEqual(previous_text.text, form_data['text'])
        self.assertNotEqual(previous_text.group, form_data['group'])
