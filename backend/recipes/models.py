from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.validators import HexValidator
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


MAX_LENGHT = 200
MAX_LENGHT_COLOR = 7
MIN_VALUE_VALID = 1
MAX_VALUE_COOKING = 1440
MAX_VALUE_AMOUNT = 10000


class Recipe(models.Model):
    """Модель управления рецептами."""

    name = models.CharField(max_length=MAX_LENGHT, verbose_name='Название')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации'
    )
    image = models.ImageField(
        upload_to='recipes/images',
        blank=True,
        null=True,
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Текст рецепта')
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='Тэги'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='ingredients',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_VALID),
            MaxValueValidator(MAX_VALUE_COOKING)
        ]
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Модель для управления тэгами рецептов."""

    name = models.CharField(
        max_length=MAX_LENGHT,
        unique=True,
        verbose_name='Тэг')
    color = models.CharField(
        max_length=MAX_LENGHT_COLOR,
        unique=True,
        validators=[HexValidator])
    slug = models.SlugField(max_length=MAX_LENGHT, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(max_length=MAX_LENGHT, verbose_name='Ингредиент')
    measurement_unit = models.CharField(max_length=MAX_LENGHT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """Связывает рецепты и ингредиенты."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_VALUE_VALID),
            MaxValueValidator(MAX_VALUE_AMOUNT)
        ]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipeingredient',
            )
        ]


class UserRecipe(models.Model):
    """Абстрактная модель связи рецепт-пользователь."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class IsFavoriteRecipe(UserRecipe):
    """Создает связь рецепт-избранное"""

    class Meta:
        default_related_name = 'is_favorite'
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_isfavorite',
            )
        ]


class ShoppingCart(UserRecipe):
    """Создает связь рецепт-список покупок"""

    class Meta:
        default_related_name = 'in_shopping_cart'
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_isshoppingcart',
            )
        ]
