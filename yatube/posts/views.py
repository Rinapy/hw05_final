from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from .utils import paginator


User = get_user_model()
POSTS_OUTPUT_COUNT: int = 10


class IndexView(ListView):
    """Возвращает главную страницу."""

    model = Post
    template_name = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = paginator(
            self.request, self.object_list, POSTS_OUTPUT_COUNT)
        context.update(
            title='Последние обновления на сайте',
            page_obj=page_obj,
        )
        return context


class GroupPostsView(ListView):
    """Возвращает посты выбранной группы."""
    model = Group
    template_name = 'posts/group_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_queryset().get(slug=self.kwargs['slug'])
        page_obj = paginator(
            self.request, group.posts.all(), POSTS_OUTPUT_COUNT)
        context.update(
            title=str(group),
            group=group,
            page_obj=page_obj
        )
        return context


def profile(request, username):
    """Выводит профайл пользователя."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_user = Post.objects.filter(author=author)
    context = {
        'title': f'Профайл пользователя {username}',
        'page_obj': paginator(request, posts_user, POSTS_OUTPUT_COUNT),
        'author': author,
        'posts_count': posts_user.count(),
        'follower_count': author.following.count(),
    }
    if request.user.is_anonymous:
        return render(request, template, context)
    elif Follow.objects.filter(
            user=request.user,
            author__username=username).exists() is False:
        context.update(following=False)
    else:
        context.update(following=True)
    return render(request, template, context)


def post_detail(request, post_id):
    """Выводит пост и информацию о нём по ID."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'title': post.text[:30],
        'post': post,
        'posts_count': post.author.posts.count(),
        'comments': post.comments.all(),
        'form': CommentForm(),
        'comments_count': post.comments.count()
    }
    return render(request, template, context)


class PostViewMixin:
    """Примись для классов редактирования и создания поста."""

    template_name = 'posts/create_post.html'
    form_class = PostForm


class PostCreateView(LoginRequiredMixin, PostViewMixin, CreateView):
    """Выводит страницу создания поста."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        author = self.request.user.username
        return reverse_lazy('posts:profile', kwargs={'username': author})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title='Добавить запись',
            card_header_name='Новый пост',
            button_text='Добавить',
        )
        return context


class PostEditView(
        PostCreateView,
        UserPassesTestMixin,
        UpdateView):
    """Выводит страницу редактирования поста."""

    model = Post

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        post_id = self.kwargs['pk']
        url = reverse_lazy('posts:post_detail', kwargs={'post_id': post_id})
        return redirect(url)

    def get_success_url(self) -> str:
        post_id = self.kwargs['pk']
        return reverse_lazy('posts:post_detail', kwargs={'post_id': post_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title='Редактировать запись',
            card_header_name='Редактировать пост',
            button_text='Сохранить',
        )
        return context


class AddCommentView(LoginRequiredMixin, CommentForm, CreateView):
    """Выводить форму коментария."""

    model = Comment

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs.get("pk"))
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        post_id = self.kwargs['pk']
        return reverse_lazy('posts:post_detail', kwargs={'post_id': post_id})


class FollowIndexView(LoginRequiredMixin, ListView):

    model = Post
    template_name = 'posts/follow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.get_queryset().filter(
            author__following__user=self.request.user)
        page_obj = paginator(
            self.request, posts, POSTS_OUTPUT_COUNT)
        context.update(
            page_obj=page_obj,
            title='Ваша лента'
        )
        return context


@login_required
def follow_to_author(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def unfollow_to_author(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username).delete()
    return redirect('posts:profile', username=username)
