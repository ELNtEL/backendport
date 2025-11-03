from django.urls import path
from .views import (
    CategoryListView,
    TagListView,
    PostListCreateView,
    PostDetailView,
    FeaturedPostsView,
    CommentListCreateView,
    MyPostsView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    # Tags
    path('tags/', TagListView.as_view(), name='tag-list'),
    
    # Posts
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/my-posts/', MyPostsView.as_view(), name='my-posts'),
    path('posts/featured/', FeaturedPostsView.as_view(), name='featured-posts'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    
    # Comments
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
]