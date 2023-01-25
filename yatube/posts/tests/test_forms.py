from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from ..models import Post, Group, Comment


User = get_user_model()


class PostCreateFormTests(TestCase):
    """Тест записи и редактирования базы данных через форму PostCreate."""
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.user_author = User.objects.create_user(username='TestUser')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_group',
            description='Тестовое описание',
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

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user_author)

    def test_create_task(self):
        """Валидная форма создает запись в Task."""
        post_count = Post.objects.count()

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
        }
        # Отправляем POST-запрос
        self.auth_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user_author,
                group=self.group
            ).exists()
        )
        
    def test_create_task_for_image(self):
        """Валидная форма создает запись в Task."""
        post_count = Post.objects.count()

        form_data = {
            'group': self.group.id,
            'text': 'Тестовый пост c картинкой',
            'image': self.uploaded
        }
        # Отправляем POST-запрос
        self.auth_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user_author,
                group=self.group,
            ).exists()
        )

    def test_edit_task(self):
        post = Post.objects.create(
            text="Тестовый текст",
            author=self.user_author,
        )
        form_data = {
            'text': 'Изменённый текстовый текст',
            'group': self.group.id,
        }
        self.auth_client.post(
            reverse('posts:edit_post', kwargs={'pk': post.id}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group,
            ).exists()
        )

    def test_create_comment(self):
        """Валидная форма создает запись в Task."""
        comment_count = Comment.objects.count()

        post = Post.objects.create(
            text='тестовый пост для коментария',
            author=self.user_author
        )

        form_data = {
            'text': 'Тестовый текст коментария',
        }
        # Отправляем POST-запрос
        self.auth_client.post(
            reverse('posts:add_comment', kwargs={'pk': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=self.user_author,
            ).exists()
        )