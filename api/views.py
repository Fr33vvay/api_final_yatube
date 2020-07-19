from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from api.permissions import IsOwnerOrReadOnly
from api.serializers import CommentSerializer, PostSerializer, \
    GroupSerializer, FollowSerializer
from api.models import Post, Group, Follow, User


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group']
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post.comments

    def perform_create(self, serializer):
        get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user)


class GroupList(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class FollowList(generics.ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'following']
    search_fields = ['=user__username', '=following__username']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        user = self.request.user
        username = self.request.data.get('following')
        if username is not None:
            following = get_object_or_404(User, username=username)
            follow_exists = user.follower.filter(following=following).exists()
            if user != following and follow_exists is False:
                if serializer.is_valid():
                    serializer.save(user=user, following=following)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
