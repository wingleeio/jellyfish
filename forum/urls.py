from django.urls import path
from . import views

urlpatterns = [
    path('api/categories/', views.categories),
    path('api/forums/', views.forums),
    path('api/threads/', views.threads),
    path('api/posts/', views.posts),
    path('', views.category_page, name='category_page'),
    path('<pk>/', views.forum_page, name='forum_page'),
    path('thread/<int:pk>/', views.thread_page, name='thread_page'),
    path('<pk>/thread_new', views.thread_new, name='thread_new'),
    path('thread/<pk>/post_new', views.post_new, name='post_new'),
    path('profile/edit', views.profile_edit, name='profile_edit'),
    path('profile/<pk>', views.profile_page, name='profile_page'),
    path('like/<tpk>/<pk>',views.like_post, name='like_post'),
    path('dislike/<tpk>/<pk>',views.dislike_post, name='dislike_post'),
    path('like/<pk>',views.like_thread, name='like_thread'),
    path('dislike/<pk>',views.dislike_thread, name='dislike_thread'),
    path('forum/<pk>/thread_remove/', views.thread_remove, name='thread_remove'),
    path('forum/thread/<pk>/post_remove', views.post_remove, name='post_remove'),
    path('forum/thread/<pk>/post_edit', views.post_edit, name='post_edit'),
    path('forum/thread/<pk>/thread_edit', views.thread_edit, name='thread_edit'),
    path('notifications', views.notifications, name='notifications'),
    path('subscribe/<pk>/',views.subscribe, name='subscribe'),
]