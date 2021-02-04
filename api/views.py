from django.db.models import Avg
from rest_framework import viewsets, filters, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from api.filters import TitleFilter
from api.models import Review, Title, Genre, Category, Comment, User
from api.permissions import (
    IsAdminOrReadOnly, IsAuthorOrModerator,
    IsAdminOnly
)
from api.serializers import (
    CommentSerializer, ReviewSerializer,
    GenreSerializer, CategorySerializer,
    UserForAdminSerializer, UserSerializer,
    TitleReadSerializer, TitleWriteSerializer
)


class CreateDestroyListRetrieveViewSet(mixins.CreateModelMixin,
                                       mixins.ListModelMixin,
                                       mixins.DestroyModelMixin,
                                       viewsets.GenericViewSet):
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserForAdminSerializer
    permission_classes = (IsAdminOnly,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    pagination_class = PageNumberPagination

    @action(
        methods=('get', 'patch'), detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request):
        user_profile = get_object_or_404(User, email=self.request.user.email)
        if request.method == 'GET':
            serializer = UserSerializer(user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            user_profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleView(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class GenreView(CreateDestroyListRetrieveViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryView(CreateDestroyListRetrieveViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title.objects, pk=title_id)
        queryset = title.reviews.all()
        return queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        user = self.request.user
        serializer.save(author=user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        title = get_object_or_404(Title.objects,
                                  pk=title_id)
        review = get_object_or_404(Review.objects,
                                   pk=review_id)
        queryset = Comment.objects.filter(title=title,
                                          review=review).all()
        return queryset

    def perform_create(self, serializer):
        """Create a new comment."""
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        title = get_object_or_404(Title.objects, pk=title_id)
        review = get_object_or_404(Review.objects, pk=review_id)
        serializer.save(author=self.request.user, title=title,
                        review=review)
