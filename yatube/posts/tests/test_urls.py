from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from ..models import Post, Group


User = get_user_model()


class TaskURLTestsPostsApp(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user_author = User.objects.create_user(username='TestUser')
        self.user_non_author = User.objects.create_user(username='TestUser2')
        self.group = Group.objects.create(
            title='Test group',
            slug='Test-group-slug',
            description='Test group description'
        )
        self.post = Post.objects.create(
            text='Test post',
            author=self.user_author,
            group=self.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_non_author = Client()
        self.authorized_client_author.force_login(self.user_author)
        self.authorized_client_non_author.force_login(self.user_non_author)

    def test_list_public_url_authorized_client(self):
        """Общедоступные страницы доступны авторизованным пользователям."""
        response_urls = [
            '/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.id}/',
            f'/profile/{self.user_author.username}/'
        ]
        for address in response_urls:
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertEqual(response.status_code, 200)

    def test_list_post_url_authorized_client_author(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client_author.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_url_authorized_client_author(self):
        """Страницы редактирования поста доступна автору."""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_url_redirect_authorized_client_non_author(self):
        """Страница редактирования поста не доступна не автору поста."""
        response = self.authorized_client_non_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_list_public_url_anonymous(self):
        """Общедоступные страницы доступны анонимному пользователею."""
        response_urls = [
            '/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.id}/',
            f'/profile/{self.user_author.username}/'
        ]
        for address in response_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_list_url_redirects_anonymus(self):
        """Страницы доступные только авторизованному
        пользователю и автору поста."""
        create_post = {'/create/': '/auth/login/?next=/create/'}
        edit_post = {f'/posts/{self.post.id}/edit/': f'/posts/{self.post.id}/'}
        response_urls = {
            'create_post': create_post,
            'edit_post': edit_post,
        }
        for response_method, response_dict in response_urls.items():
            for response_address, expected_redirect in response_dict.items():
                with self.subTest(response_method=response_method):
                    response = self.guest_client.get(response_address)
                    self.assertRedirects(response, expected_redirect)

    def test_unexisting_url_anonymus_and_authorized_client(self):
        """Несуществующие страницы для пользователя выдают 404."""
        response = self.authorized_client_author.get('/unexsisting/')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user_author.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_comment_only_auth_user(self):
        """Коментировать пост может только авторизованный пользователь."""
        response = self.guest_client.get(f'/posts/{self.post.id}/comment/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')
