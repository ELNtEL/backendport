from django.shortcuts import render
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Category, Tag, Comment
from .serializers import(
    PostListSerializer,
    CategorySerializer,
    PostDetailSerializer,
    TagSerializer,
    CommentSerializer
    

)
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_featured', 'category', 'tags', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'published_at', 'views_count', 'title']
    ordering = ['-published_at', '-created_at']
    
    def get_queryset(self):
        queryset = Post.objects.all()
        # Only show published posts to non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostDetailSerializer
        return PostListSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count +=1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.AllowAny()]
class MyPostsView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes =[permissions.IsAuthenticated]
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
class FeaturedPostsView(generics.ListAPIView):
    queryset = Post.objects.filter(is_featured=True,status='published')
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id, is_approved=True)
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        if self.request.user.is_authenticated:
            serializer.save(post_id=post_id, author=self.request.user)
        else:
            serializer.save(post_id=post_id)

        