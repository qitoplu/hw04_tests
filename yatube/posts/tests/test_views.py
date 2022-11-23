from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Post, Group
from ..views import POSTS_QUANTITY

POSTS_OVERALL = 13
User = get_user_model()


class PostPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html'
        }
        for address, template in templates_pages_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def same_obj(self, post1, post2):
        self.assertEqual(post2.text, post1.text)
        self.assertEqual(post2.group, post1.group)
        self.assertEqual(post2.author, post1.author)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:index'
        ))
        post = response.context['page_obj'][0]
        self.same_obj(post, self.post)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        ))
        post = response.context['page_obj'][0]
        self.same_obj(post, self.post)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ))
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object.author, self.user)
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.pub_date, self.post.pub_date)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').group, self.group)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create'
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post, index)
        self.assertIn(self.post, group)
        self.assertIn(self.post, profile)


class TestPaginator(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user('test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        posts_list = []
        for i in range(POSTS_OVERALL):
            posts_list.append(Post(
                author=self.user,
                text=f'Текстовый текст {i}',
                group=self.group,
                pk=i
            ))
        self.post = Post.objects.bulk_create(posts_list)

    def test_paginator_works_guest(self):
        pages = (reverse('posts:index'),
                 reverse('posts:profile', kwargs={'username': self.user}),
                 reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        for page in pages:
            response_first = self.guest_client.get(page)
            response_second = self.guest_client.get(page + '?page=2')
            count_posts_first = len(response_first.context['page_obj'])
            count_posts_second = len(response_second.context['page_obj'])
            self.assertEqual(
                count_posts_first,
                POSTS_QUANTITY
            )
            self.assertEqual(
                count_posts_second,
                POSTS_OVERALL - POSTS_QUANTITY
            )

    def test_paginator_works_authorized(self):
        pages = (reverse('posts:index'),
                 reverse('posts:profile', kwargs={'username': self.user}),
                 reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        for page in pages:
            response_first = self.authorized_client.get(page)
            response_second = self.authorized_client.get(page + '?page=2')
            count_posts_first = len(response_first.context['page_obj'])
            count_posts_second = len(response_second.context['page_obj'])
            self.assertEqual(
                count_posts_first,
                POSTS_QUANTITY
            )
            self.assertEqual(
                count_posts_second,
                POSTS_OVERALL - POSTS_QUANTITY
            )
