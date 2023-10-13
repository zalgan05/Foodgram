import webcolors
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Ingredient, IsFavoriteRecipe, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import Follow

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Возвращает объекты модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.following.filter(user=user).exists()
        return False


class NameColor2Hex(serializers.Field):
    """Преобразует название цвета в HEX-формат."""

    def to_representation(self, value):
        try:
            value = webcolors.name_to_hex(value)
        except ValueError:
            raise serializers.ValidationError('Для этого имени нет цвета')
        return value


class TagSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Tag."""

    color = NameColor2Hex()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Обрабатывает ингредиенты в рецептах."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Recipe."""

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set'
    )
    author = CustomUserSerializer()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if self.context.get('request').user.is_authenticated:
            return obj.is_favorite.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if self.context.get('request').user.is_authenticated:
            return obj.in_shopping_cart.filter(user=user).exists()
        return False


class RecipeCreateAndUpdateSerializer(serializers.ModelSerializer):
    """Добавляет/обновляет объект модели Recipe."""

    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'cooking_time',
            'text',
            'tags',
            'name',
            'ingredients',
            'image'
        )

    def create_ingredients(self, instance, ingredients_data):
        """Добавление ингредиентов к рецепту."""
        data = []
        for ingredient in ingredients_data:
            ingredient_data = ingredient['ingredient']
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient_data['id']
            )
            RecIng = RecipeIngredient(
                recipe=instance,
                ingredient=current_ingredient,
                amount=ingredient['amount']
            )
            data.append(RecIng)
        RecipeIngredient.objects.bulk_create(data)

    def validate(self, attrs):
        data = []
        for ingredients in attrs.get('ingredients'):
            if ingredients['ingredient']['id'] in data:
                raise serializers.ValidationError(
                    'Ингредиент уже добавлен в рецепт'
                )
            else:
                data.append(ingredients['ingredient']['id'])
        return super().validate(attrs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        instance.tags.set(tags)

        self.create_ingredients(instance, ingredients_data)
        return instance

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class IsFavoriteSerializer(serializers.ModelSerializer):
    """Создает связь рецепт-избранное."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']

    def create(self, validated_data):
        recipe_id = self.context.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        IsFavoriteRecipe.objects.create(
            user=self.context.get('request').user,
            recipe=recipe
        )
        return recipe

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        recipe_id = self.context.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.method == 'POST':
            if IsFavoriteRecipe.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже добавили рецепт в избранное'
                )
        else:
            if not IsFavoriteRecipe.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    {'errors': 'Вы не добавляли этот рецепт в избранное'},
                )
        return super().validate(attrs)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Создает связь рецепт-список покупок."""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['id', 'name', 'image', 'cooking_time']

    def create(self, validated_data):
        recipe_id = self.context.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingCart.objects.create(
            user=self.context.get('request').user,
            recipe=recipe
        )
        return recipe

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user
        recipe_id = self.context.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже добавили рецепт в список покупок'
                )
        else:
            if not ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    {'errors': 'Вы не добавляли этот рецепт в список покупок'},
                )
        return super().validate(attrs)


class CustomUserCreateSerializer(UserCreateSerializer):
    """Добавляет объект модели User."""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class RecipeForSubscribe(serializers.ModelSerializer):
    """Вывод объекта модели Recipe для подписок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetSubscriptionsSerializer(CustomUserSerializer):
    """Возвращает объекты модели User подписок текущего пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeForSubscribe(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CreateSubscribeSerializer(serializers.ModelSerializer):
    """Добавляет пользователя в подписки."""

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, attrs):
        user = attrs['user']
        follow_user = attrs['following']
        if user == follow_user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        elif user.follower.filter(following=follow_user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return super().validate(attrs)

    def to_representation(self, instance):
        instance = User.objects.get(id=self.context.get('pk'))
        return GetSubscriptionsSerializer(
            instance, context={'request': self.context.get('request')}
        ).data
