from django.urls import path
from . import views


app_name = 'posts'

urlpatterns = [
    # Главная страницы сайта
    path('', views.index, name='index'),
    # Записи группы
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # Профайл пользователя
    path('profile/<str:username>/', views.profile, name='profile'),
    # Просмотр поста
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Создание поста
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    # Редактирование поста
    path('posts/<int:pk>/edit/',
         views.PostEditView.as_view(),
         name='edit_post'
         ),
    path('posts/<int:pk>/comment/',
         views.AddCommentView.as_view(), name='add_comment'),
    path('follow/', views.FollowIndexView.as_view(), name='follow')
]
