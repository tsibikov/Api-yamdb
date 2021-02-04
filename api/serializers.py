from rest_framework import serializers, exceptions

from .models import (
    Comment, Review, Title,
    Category, Genre, User
)


class UserForAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",
                  "bio", "email", "role")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",
                  "bio", "email", "role")
        read_only_fields = ("role", "email")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre

    def to_representation(self, obj):
        return {
            "name": obj.name,
            "slug": obj.slug
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category

    def to_representation(self, obj):
        return {
            "name": obj.name,
            "slug": obj.slug
        }


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField()

    class Meta:
        fields = ("id", "name", "year", "genre", "rating",
                  "category", "description")
        read_only_fields = ("id", "rating")
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        required=False,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug",
        required=False,
        queryset=Category.objects.all()
    )

    class Meta:
        fields = ("id", "name", "year", "genre",
                  "category", "description")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date",)
        read_only_fields = ("id", "author", "pub_date")
        model = Review

    def validate(self, data):
        if self.context['view'].action != "create":
            return data
        title_id = self.context['view'].kwargs.get("title_id")
        user = self.context['request'].user
        if Review.objects.filter(author=user, title_id=title_id).exists():
            raise exceptions.ValidationError("Отзыв уже был оставлен.")
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username",
                                          read_only=True)

    class Meta:
        fields = ("id", "text", "author", "pub_date",)
        read_only_fields = ("id", "author", "pub_date",)
        model = Comment
