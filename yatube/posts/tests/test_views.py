from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache, caches
from ..models import Post, Group
from ..forms import PostForm


User = get_user_model()


class TestViewsPostsApp(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user_author = User.objects.create_user(username='TestUser')
        self.group = Group.objects.create(
            title='Test group',
            slug='Test-group-slug',
            description='Test group description'
        )
        self.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='image.png',
            content=self.image,
            content_type='image'
        )
        self.post = Post.objects.create(
            text='Test post',
            author=self.user_author,
            group=self.group,
            image=self.uploaded
        )

    def setUp(self):

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)
        cache.clear()

    def test_namespace_uses_correct_template(self):
        """Namespace'ы используют коректные шаблоны."""
        namespace_dict = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.user_author.username
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            reverse('posts:edit_post', kwargs={
                'pk': self.post.id
            }): 'posts/create_post.html'
        }
        for namespace, template in namespace_dict.items():
            with self.subTest(namespace=namespace):
                response = self.authorized_client_author.get(namespace)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правельным котекстом."""
        response = self.authorized_client_author.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post, self.post)
        post_context = {
            first_post.text: self.post.text,
            first_post.author.username: self.post.author.username,
            first_post.pub_date: self.post.pub_date,
            first_post.group.slug: self.post.group.slug,
            first_post.id: self.post.id,
            first_post.image: self.post.image
        }
        for expected, org_contex in post_context.items():
            with self.subTest(expected=expected):
                self.assertEqual(org_contex, expected)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правельным котекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.group.slug, self.group.slug)

    def test_profile_user_show_correct_context(self):
        """Шаблон profile сформирован с правельным котекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:profile', kwargs={
                'username': self.user_author.username
            }))
        first_post = (
            response.context['page_obj'][0])
        self.assertEqual(first_post.author.username, self.user_author.username)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правельным котекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        expected_post = response.context['post']
        self.assertEqual(expected_post.id, self.post.id)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правельным котекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:create_post'))
        form_obj = response.context.get('form')
        self.assertIsInstance(form_obj, PostForm)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правельным котекстом."""
        response = self.authorized_client_author.get(reverse(
            'posts:edit_post',
            kwargs={'pk': self.post.id}))
        form_obj = response.context.get('form')
        self.assertIsInstance(form_obj, PostForm)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user_author = User.objects.create_user(username='TestUser')
        self.group = Group.objects.create(
            title='Test group',
            slug='Test-group-slug',
            description='Test group description'
        )
        self.posts_list = []
        i = 1
        for i in range(1, 14):
            self.posts_list.append(Post.objects.create(
                text=f'Test post {i}',
                author=self.user_author,
                group=self.group)
            )
            i += 1

    def setUp(self):

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_author)
        cache.clear()

    def test_paginator_index_page(self):
        """Paginator index работает верно"""
        pages_response = {
            len(self.authorized_client_author.get(reverse(
                'posts:index'))
                .context['page_obj']): 10,
            len(self.authorized_client_author.get(reverse(
                'posts:index') + '?page=2')
                .context['page_obj']): 3
        }
        for response_len, expected_len in pages_response.items():
            with self.subTest(pages_response=pages_response):
                self.assertEqual(response_len, expected_len)

    def test_paginator_group_list_page(self):
        """Paginator group_list работает верно"""
        pages_response = {
            len(self.authorized_client_author.get(
                reverse(
                    'posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    })).context['page_obj']): 10,
            len(self.authorized_client_author.get(
                reverse(
                    'posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    }
                ) + '?page=2').context['page_obj']): 3
        }
        for response_len, expected_len in pages_response.items():
            with self.subTest(pages_response=pages_response):
                self.assertEqual(response_len, expected_len)

    def test_paginator_profile_page(self):
        """Paginator profile работает верно"""
        pages_response = {
            len(self.authorized_client_author.get(
                reverse(
                    'posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    }
                )).context['page_obj']): 10,
            len(self.authorized_client_author.get(
                reverse(
                    'posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    }
                ) + '?page=2')
                .context['page_obj']): 3
        }
        for response_len, expected_len in pages_response.items():
            with self.subTest(pages_response=pages_response):
                self.assertEqual(response_len, expected_len)

    def test_posts_create_in_index_profile_page(self):
        """Пост поподает на гланую и профайл страницы."""
        self.post_test = Post.objects.create(
            text='Test post page index and profile',
            author=self.user_author,
        )
        response_url = {
            'index': reverse('posts:index'),
            'profile': reverse(
                'posts:profile',
                kwargs={
                    'username': self.user_author.username
                })
        }
        for page, url_page in response_url.items():
            with self.subTest(page=page):
                response = (self.authorized_client_author.get(url_page)
                            .context['page_obj'][0]
                            )
                self.assertEqual(response.text, self.post_test.text)

    def test_post_not_in_group(self):
        """Пост не попадает в непредназначенную группу."""
        self.post_test = Post.objects.create(
            text='Test post page index and profile',
            author=self.user_author,
        )
        response = (self.authorized_client_author.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}))
            .context['page_obj'][0]
        )
        self.assertNotEqual(response.text, self.post_test.text)


class CaheTest(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user = User.objects.create_user(username='TestUser')

        self.post = Post.objects.create(
            text='Test post 1',
            author=self.user,
        )

    def setUp(self):

        self.user = Client()
        cache.clear()

    def test_cache_index_page(self):
        """Тест кэша страницы index"""
        first_cache = self.user.get(reverse('posts:index')).content
        Post.objects.filter(id=1).delete()
        cache.clear()
        second_cache = self.user.get(reverse('posts:index')).content
        self.assertTrue(first_cache, second_cache)
