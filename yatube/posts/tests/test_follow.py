from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from ..models import Post, Follow


User = get_user_model()


class TestViewsPostsApp(TestCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user_author = User.objects.create_user(username='TestUser')
        self.user_follower = User.objects.create_user(username='Follower')
        self.user_not_follower = User.objects.create_user(
            username='Not_Follower')
        self.post = Post.objects.create(
            text='Test post',
            author=self.user_author,
        )

    def setUp(self):

        self.authorized_client_author = Client()
        self.authorized_user_follower = Client()
        self.authorized_user_not_follower = Client()
        self.authorized_client_author.force_login(self.user_author)
        self.authorized_user_follower.force_login(self.user_follower)
        self.authorized_user_not_follower.force_login(self.user_not_follower)
        cache.clear()

    def test_follow_system(self):
        """Тест подписки на автора"""

        response = self.authorized_user_follower.get(
            f'/profile/{self.user_author.username}/follow/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Follow.objects.filter(
            user=self.user_follower, author=self.user_author))

        response = self.authorized_user_follower.get(
            f'/profile/{self.user_author.username}/unfollow/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower, author=self.user_author))

    def test_follow_page(self):
        """Подписки отображаються верно"""

        self.authorized_user_follower.get(
            f'/profile/{self.user_author.username}/follow/')
        response = self.authorized_user_follower.get('/follow/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)

        response = self.authorized_user_not_follower.get('/follow/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 0)
