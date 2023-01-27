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
        context['title'] = 'Последние обновления на сайте'
        context['page_obj'] = paginator(self.request , self.object_list, POSTS_OUTPUT_COUNT)
        return context
        
class GroupPostsView(ListView):
    """Возвращает посты выбранной группы."""
    model = Group
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        self.group = Group.objects.get(slug=self.kwargs['slug'])
        return self.group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = paginator(self.request, self.object_list.posts.all(), POSTS_OUTPUT_COUNT)
        context['title'] = str(self.group)
        context['group'] = self.group
        return context



def profile(request, username):
    """Выводит профайл пользователя."""
    template = 'posts/profile.html'
    title = f'Профайл пользователя {username}'
    author = get_object_or_404(User, username=username)
    posts_user = Post.objects.filter(author=author)
    posts_count = Post.objects.filter(author=author).count()
    page_obj = paginator(request, posts_user, POSTS_OUTPUT_COUNT)
    if Follow.objects.filter(user=request.user, author__username=username) == 'None':
        following = False
    else:
        following = True

    context = {
        'title': Follow.objects.filter(user=request.user, author__username=username) == Follow.DoesNotExist,
        'page_obj': page_obj,
        'author': author,
        'posts_count': posts_count,
        'following': following
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


class FollowIndexView(LoginRequiredMixin, ListView):
    
    
    model = Follow
    template_name = 'posts/follow.html'


    def get_queryset(self):
        try:
            self.object_list = Follow.objects.get(user_id=self.request.user)
        except Follow.DoesNotExist:
            self.object_list = None
        return self.object_list
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object_list == None:
            context['page_obj'] = None
            context['title'] = 'Подпишитесь, что бы следить за последними обновлениями'
        else:   
            context['page_obj'] = paginator(self.request, self.object_list.author.posts.all(), POSTS_OUTPUT_COUNT)
            context['title'] = 'Ваша лента'
        return context

@login_required
def follow_to_author(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


class UnFollowToAuthor(LoginRequiredMixin, UpdateView):
    pass