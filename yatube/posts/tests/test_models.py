from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """У модели корректно работает метод __str__."""
        task = PostModelTest
        str_method_verboses = {
            str(task.post): task.post.text[:15],
            str(task.group): f'Посты группы "{task.group.title}"'
        }

        for string_method, excpected_value in str_method_verboses.items():
            with self.subTest(string_method=string_method):
                self.assertEqual(string_method, excpected_value)

    def test_models_verbose_names(self):
        """Ожидаемые verboses_name у моделей."""
        task = PostModelTest.post

        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name,
                    expected_value)

    def test_models_help_text(self):
        """Ожидаемые help_text у моделей."""
        task = PostModelTest.post

        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text,
                    expected_value)
