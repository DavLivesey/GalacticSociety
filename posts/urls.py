from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('follow/', views.follow_index, name='follow_index'),
    path('new/', views.new_post, name='new_post'),
    path('group/<slug:slug>/', views.group_posts, name="group_posts"),
    path('group/', views.groups, name='group'),       
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
        ),
    path('<str:username>/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'
        ),
    path('<str:username>/follow/', views.profile_follow, name='profile_follow'),
    path('<str:username>/unfollow/', views.profile_unfollow, name='profile_unfollow'),
    path(
        '<str:username>/<int:post_id>/delete',
        views.post_delete,
        name='post_delete'
        ),
    path(
        '<str:username>/profile_edit',
        views.profile_edit,
        name='profile_edit'
    ),
    path(
        '<str:username>/following_view/',
        views.following_view,
        name='following_view'
    ),
    path(
        '<str:username>/follower_view/',
        views.follower_view,
        name='follower_view'
    ),
    path(
        '<str:username>/<int:post_id>/plus', views.rating_plus, name='rating_plus'
    ),
    path(
        '<str:username>/<int:post_id>/minus', views.rating_minus, name='rating_minus'
    )
]
