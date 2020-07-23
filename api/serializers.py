from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Comment, Follow, Group, Post, User


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    group = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        fields = '__all__'
        model = Comment


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'title']
        model = Group


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(
        default=serializers.CurrentUserDefault())
    following = serializers.SlugRelatedField(queryset=User.objects.all(),
                                             slug_field='username')

    def validate(self, data):
        user = self.context['request'].user
        if user == data['following']:
            raise serializers.ValidationError('Нельзя подписаться '
                                              'на себя самого')
        return data

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(queryset=Follow.objects.all(),
                                    fields=('user', 'following'))
        ]
