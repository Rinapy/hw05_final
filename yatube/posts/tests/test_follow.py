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
        self.user_follower = User.objects.create_user(username='Follower')
        self.post = Post.objects.create(
            text='Test post',
            author=self.user_author,
        )

    def setUp(self):

        self.authorized_client_author = Client()
        self.authorized_user_follower = Client()
        self.authorized_client_author.force_login(self.user_author)
        self.authorized_user_follower.force_login(self.user_follower)
