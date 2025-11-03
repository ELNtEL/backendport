from rest_framework import serializers
from .models import Post, Category, Tag, Comment

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'despcription', 'post_count', 'created_at']

        def get_post_count(self, obj):
            return obj.posts.filter(status='published').count

class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)


    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'name', 'email', 'content', 'is_approved', 'created_at']
        read_only_fields = ['id', 'author', 'is_approved', 'created_at']
    

class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'author_name', 'category', 'category_name', 
            'tags', 'status', 'is_featured', 'views_count', 
            'comment_count', 'published_at', 'created_at'
        ]
    
    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()


class PostDetailSerializer(serializers.ModelSerializer):
   author_name = serializers.CharField(source='author.full_name', read_only=True)
   Category_name = serializers.CharField(source='category.name', read_only = True)
   tags = TagSerializer(many=True, read_only=True)
   tag_ids = serializers.PrimaryKeyRelatedField(
       querset=Tag.objects.all(),
       many=True,
       write_only=True,
       required=False
   )
   comments = CommentSerializer(many=True, read_only=True)
   comment_count = serializers.SerializerMethodField()
   class Meta:
       model = Post
       fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'author', 'author_name', 'category', 'category_name',
            'tags', 'tag_ids', 'status', 'is_featured', 'views_count', 
            'comments', 'comment_count', 'published_at', 
            'created_at', 'updated_at'
       ]
       read_only_fields = ['id', 'author', 'slug', 'views_count', 'created_at', 'updated_at']

       def get_comment_count(self, obj):
           return obj.comments.filter(is_approved=True).count()
       def create(self, validated_data):
           tag_ids = validated_data.pop('tag_ids', [])
           user = self.context['request'].user
           post = Post.objects.create(author=user, **validated_data)
           post.tags.set(tag_ids)
           return post
       def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        return instance
     
        



    


    
