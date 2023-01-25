from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from .utils import paginator


User = get_user_model()
POSTS_OUTPUT_COUNT: int = 10


def index(request):
    """Возвращает главную страницу"""
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts_list = Post.objects.all()
    page_obj = paginator(request, posts_list, POSTS_OUTPUT_COUNT)
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Возвращает посты выбранной группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = paginator(request, posts_list, POSTS_OUTPUT_COUNT)
    context = {
        'title': str(group),
        'page_obj': page_obj,
        'group': group,
    }

    return render(request, template, context)


def profile(request, username):
    """Выводит профайл пользователя."""
    template = 'posts/profile.html'
    title = f'Профайл пользователя {username}'
    author = get_object_or_404(User, username=username)
    posts_user = Post.objects.filter(author=author)
    posts_count = Post.objects.filter(author=author).count()
    page_obj = paginator(request, posts_user, POSTS_OUTPUT_COUNT)
    context = {
        'title': title,
        'page_obj': page_obj,
        'author': author,
        'posts_count': posts_count
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Выводит пост и информацию о нём по ID."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    comments = post.comments.all()
    form = AddCommentView
    title = post.text[:30]
    context = {
        'title': title,
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
        'comments_count': post.comments.count()
    }
    return render(request, template, context)


class PostViweMixin:
    """Примись для классов редактирования и создания поста."""

    template_name = 'posts/create_post.html'
    form_class = PostForm


class PostCreateView(LoginRequiredMixin, PostViweMixin, CreateView):
    """Выводит страницу создания поста."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        author = self.request.user.username
        return reverse_lazy('posts:profile', kwargs={'username': author})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить запись'
        context['card_header_name'] = 'Новый пост'
        context['button_text'] = 'Добавить'
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
        context['title'] = 'Редактировать запись'
        context['card_header_name'] = 'Редактировать пост'
        context['button_text'] = 'Сохранить'
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


class FollowIndexView(LoginRequiredMixin, CreateView):
    
    
    model = Follow
    fields = '__all__'
    template_name = 'posts/follow.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = paginator(self.request, Post.objects.filter(author_id=self.request.user)(), POSTS_OUTPUT_COUNT)
        return context