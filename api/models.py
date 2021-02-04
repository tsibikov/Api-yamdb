from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    ADMIN = "admin", "Администратор"
    MODERATOR = "moderator", "Модератор"
    USER = "user", "Пользователь"


class User(AbstractUser):
    email = models.EmailField("e-mail", unique=True)
    username = models.CharField("Имя пользователя", max_length=50,
                                blank=True, null=True, unique=True)
    bio = models.TextField("О себе", blank=True, null=True)
    role = models.CharField("Роль пользователя", max_length=10,
                            choices=UserRole.choices, default=UserRole.USER)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)

    class Meta:
        ordering = ("username",)


class Genre(models.Model):
    name = models.TextField(unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.name, self.slug}"

    class Meta:
        ordering = ("-pk",)


class Category(models.Model):
    name = models.TextField(unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.name, self.slug}"

    class Meta:
        ordering = ("-pk",)


class Title(models.Model):
    name = models.TextField("Название", )
    year = models.PositiveIntegerField("Год выпуска", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField("Genre", related_name="genres", blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE,
                                 related_name="categories", blank=True, null=True)

    class Meta:
        ordering = ("-pk",)


class Review(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name="reviews", null=False)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="reviews", null=False)
    score = models.PositiveIntegerField(
        "Оценка", null=False,
        validators=[MinValueValidator(1, "Не меньше 1"),
                    MaxValueValidator(10, "Не больше 10")]
    )
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-pub_date",)


class Comment(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name="comments", null=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name="comments", null=False)
    text = models.TextField(null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments", null=False)
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-pub_date",)
