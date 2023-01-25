from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Илюстрация поста'
        }


class CommentForm(forms.ModelForm):
    """Форма коментария."""

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст коментария'
        }
