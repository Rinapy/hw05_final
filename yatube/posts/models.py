from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    """Модель поста."""

    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='post/',
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.text[:15]}'

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Group(models.Model):
    """Модель группы."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField()

    def __str__(self) -> str:
        return f'Посты группы "{self.title}"'

class Comment(models.Model):
    """Модель комментариев."""
    
    text = models.TextField(max_length=240)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор коментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete= models.CASCADE,
        related_name='comments',
    )
    created = models.DateTimeField(auto_now_add=True)